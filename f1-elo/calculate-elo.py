import hashlib
import json
import math
import numpy as np
import pandas as pd
from dataclasses import dataclass, asdict as dataclass_asdict
from datetime import datetime
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

import dataset

def sorted_race_ids(*, dataset_path):
    races = pd.read_csv(dataset_path / "races.csv")
    return list(races.sort_values("date")[["raceId", "date"]].itertuples(index=False))


def get_races_results(*, dataset_path):
    data = pd.read_csv(dataset_path / "results.csv")
    results = defaultdict(list)
    for result in data.itertuples():
        results[result.raceId].append((result.positionOrder, result.driverId, result.constructorId))
    return {
        race_id: [(driver, team) for _, driver, team in sorted(drivers)]
        for race_id, drivers in results.items()
    }


def get_drivers_names(*, dataset_path):
    drivers = pd.read_csv(dataset_path / "drivers.csv")
    return {
        driver.driverId: f"{driver.forename} {driver.surname}"
        for driver in drivers.itertuples()
    }


def get_teams_names(*, dataset_path):
    teams = pd.read_csv(dataset_path / "constructors.csv")
    return {
        team.constructorId: team.name
        for team in teams.itertuples()
    }


@lru_cache(maxsize=None)
def date_to_year(date):
    return int(date.split("-")[0])


@lru_cache(maxsize=None)
def date_minus_years(date, years):
    year, month, day = map(int, date.split("-"))
    return f"{year - years:04d}-{month:02d}-{day:02d}"


def zscore(*, values, value):
    mean = sum(values) / len(values)
    stddev = math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))
    if stddev < 1e-9:
        return 0
    return (value - mean) / stddev


@dataclass
class DatasetStats:
    MIN_YEAR: int | None = None
    MAX_YEAR: int | None = None

    @classmethod
    def make(cls, *, race_ids):
        res = cls()
        for race in race_ids:
            year = date_to_year(race.date)
            if res.MIN_YEAR is None or res.MIN_YEAR > year:
                res.MIN_YEAR = year
            if res.MAX_YEAR is None or res.MAX_YEAR < year:
                res.MAX_YEAR = year
        return res


class Elos:
    def __init__(self, *, params):
        self.params = params
        self.elos = dict()
        self.elos_by_driver_by_date = defaultdict(dict)

    def prob_win(self, elo_a, elo_b):
        return 1. / (1 + math.pow(self.params.PROB_BASE, (elo_b - elo_a) * self.params.PROB_SCALE))

    def _update_rank(self, *, driver, delta, race_date, team):
        self.elos[driver] += delta
        self.elos_by_driver_by_date[race_date][driver] = (self.elos[driver], team)

    def active_elos_by_date(self, *, date):
        start_window_date = date_minus_years(date, self.params.YEARS_BACK - 1)
        elos_by_date_by_driver = defaultdict(list)
        for race_date in self.elos_by_driver_by_date:
            if start_window_date <= race_date <= date:
                for driver, (elo, _) in self.elos_by_driver_by_date[race_date].items():
                    elos_by_date_by_driver[driver].append((race_date, elo))
        return [
            max(driver_elos)[1]
            for driver_elos in elos_by_date_by_driver.values()
        ]

    def avg_active_elo_by_date(self, *, date):
        return np.mean(self.active_elos_by_date(date=date))

    def pick_z_score_by_driver_with_elo_and_date(self, *, driver):
        global_min_date = min(self.elos_by_driver_by_date.keys())
        active_dates = sorted(set(
            date
            for date, elos_by_driver in self.elos_by_driver_by_date.items()
            if driver in elos_by_driver
        ))
        elos_by_date = {date: self.active_elos_by_date(date=date) for date in active_dates}
        candidates = [
            (
                zscore(
                    value=self.elos_by_driver_by_date[date][driver][0],
                    values=elos_by_date[date]),
                self.elos_by_driver_by_date[date][driver][0],
                date,
                self.elos_by_driver_by_date[date][driver][1],
            )
            for date in active_dates
            if date_to_year(date) >= self.params.PROF_YEAR + self.params.YEARS_BACK
        ]
        if not candidates:
            return 0, self.elos[driver], global_min_date, None
        return max(candidates)


    def update(self, *, race_date, drivers_order):
        n = len(drivers_order)
        team_of_driver = {driver: team for driver, team in drivers_order}
        drivers_order = [driver for driver, _ in drivers_order]

        for driver in drivers_order:
            if driver not in self.elos:
                self.elos[driver] = self.params.INITIAL_ELO

        def driver_rank(driver, driver_elo):
            return n - sum(
                self.prob_win(driver_elo, self.elos[other])
                for other in drivers_order
                if other != driver
            )

        exp_ranks = {
            driver: driver_rank(driver, self.elos[driver])
            for driver in drivers_order
        }
        actual_rank = {
            driver: 1 + i
            for i, driver in enumerate(drivers_order)
        }
        def calculate_new_elo(driver):
            target_rank = math.sqrt(exp_ranks[driver] * actual_rank[driver])
            L, R = self.params.MIN_ELO, self.params.MAX_ELO
            for i in range(100):
                if R - L < self.params.ELO_EPSILON:
                    break
                M = (L + R) / 2
                if driver_rank(driver, M) < target_rank:
                    R = M
                else:
                    L = M
            new_elo = min([L, R], key=lambda x: abs(driver_rank(driver, x) - target_rank))
            return new_elo

        deltas = {
            driver: (calculate_new_elo(driver) - self.elos[driver]) * self.params.DELTA_SCALE
            for driver in drivers_order
        }
        avg_delta = sum(deltas.values()) / n
        deltas = {
            driver: delta - avg_delta
            for driver, delta in deltas.items()
        }

        for driver, delta in deltas.items():
            self._update_rank(
                driver=driver,
                delta=delta,
                race_date=race_date,
                team=team_of_driver[driver])


@dataclass
class Params:
    INITIAL_ELO: int = 1500
    MAX_ELO: float = 1000000
    MIN_ELO: float = 0
    ELO_EPSILON: float = 1e-9
    PROB_BASE: float = 10
    PROB_SCALE: float = 1. / 400
    DELTA_SCALE: float = 1. / 2
    YEARS_BACK: int = 5
    PROF_YEAR: int = 1979


def dump_result(*, results, params, dataset_stats):
    params = dataclass_asdict(params)
    dataset_stats = dataclass_asdict(dataset_stats)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    params_hash = hashlib.sha256(
        json.dumps(params, sort_keys=True, separators=(",", ":")
    ).encode()).hexdigest()[:8]
    result_dir = Path(__file__).parent / "results" / f"result-{timestamp}"
    result_dir.mkdir(parents=True, exist_ok=False)

    with open(result_dir / "params.json", "w") as f:
        json.dump(params, f, sort_keys=True, indent=2)
    with open(result_dir / "results.json", "w") as f:
        json.dump(results, f, sort_keys=True)
    with open(result_dir / "dataset_stats.json", "w") as f:
        json.dump(dataset_stats, f, sort_keys=True, indent=2)


def main(*, dataset_path, params=None):
    if params is None:
        params = Params()

    race_ids = sorted_race_ids(dataset_path=dataset_path)
    print(len(race_ids), "races")

    races_results = get_races_results(dataset_path=dataset_path)

    dataset_stats = DatasetStats.make(race_ids=race_ids)

    elos = Elos(params=params)

    for race_index, race in enumerate(race_ids):
        if race_index % 100 == 0:
            print(f"Processing race {race_index + 1}/{len(race_ids)}")
        race_id, race_date = race.raceId, race.date

        race_results = races_results.get(race_id, None)
        if race_results is None:
            print("No results for race", race_id)
            continue
        elos.update(race_date=race_date, drivers_order=race_results)

    def sort_key(driver_id):
        zscore, elo, date, team = elos.pick_z_score_by_driver_with_elo_and_date(driver=driver_id)
        return -zscore, elo, date, team

    ordered_drivers = sorted(elos.elos.keys(), key=sort_key)
    driver_names = get_drivers_names(dataset_path=dataset_path)
    team_names = get_teams_names(dataset_path=dataset_path)

    drivers_data = []
    for i, driver_id in enumerate(ordered_drivers):
        zscore, elo, date, team = elos.pick_z_score_by_driver_with_elo_and_date(driver=driver_id)
        name = driver_names.get(driver_id, f"(John Doe)")
        team_name = team_names.get(team, f"(Unknown Team)")
        drivers_data.append({
            "team": team_name,
            "name": name,
            "zscore": zscore,
            "elo": elo,
            "date": date
        })
    dump_result(results=drivers_data, params=params, dataset_stats=dataset_stats)

    data_to_show = []
    for i, data in enumerate(drivers_data[:40]):
        team, name, zscore, elo, date = data["team"], data["name"], data["zscore"], data["elo"], data["date"]
        data_to_show.append((str(i + 1), f"[{team}]", name, zscore, elo, date))

    max_idx_length = max(len(id) for id, _, _, _, _, _ in data_to_show)
    max_team_length = max(len(team) for _, team, _, _, _, _ in data_to_show)
    max_name_length = max(len(name) for _, _, name, _, _, _ in data_to_show)
    print(f"Top {len(data_to_show)} drivers by ELO (out of {len(ordered_drivers)}):")
    for id, team, name, zscore, elo, date in data_to_show:
        id = id.rjust(max_idx_length)
        team = team.ljust(max_team_length)
        name = name.ljust(max_name_length)
        print(f"{id}. {team} {name}   pick zscore  {zscore:.2f}  with ELO  {elo:.2f}  at  {date}")

    # print("Avg ELOs by year matplotlib plot:")
    # import matplotlib.pyplot as plt
    # years = []
    # avg_elos = []
    # for year in sorted(elos.elos_by_driver_by_year.keys()):
    #     year_elos = elos.elos_by_driver_by_year[year]
    #     avg_elo = sum(year_elos.values()) / len(year_elos)
    #     years.append(year)
    #     avg_elos.append(avg_elo)
    # plt.plot(years, avg_elos)
    # plt.xlabel("Year")
    # plt.ylabel("Average ELO")
    # plt.title("Avg ELOs by year")
    # plt.show()


if __name__ == "__main__":
    main(dataset_path=dataset.PATH)
