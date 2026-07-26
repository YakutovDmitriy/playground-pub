package core

import kotlin.random.Random

class GameState(grid_: Grid) {
    var grid = grid_
        private set

    init {
        grid.checkCorrect()
    }

    companion object {
        fun generateInitial(params: GameParams, rng: Random): GameState =
            GameState(emptyGrid(params.n, params.m))
                .tryAddRandomCell(rng, params.ms)
                .tryAddRandomCell(rng, params.ms)
    }

    fun copy() =
        GameState(grid.map { row -> row.map { it }.toMutableList() })

    fun swipe(type: SwipeType, mergeStrategy: MergeStrategy): GameState {
        grid = type.swipe(grid, mergeStrategy)
        return this
    }

    fun tryAddRandomCell(rng: Random, mergeStrategy: MergeStrategy, count: Int = 1): GameState {
        if (count <= 0) {
            return this
        }
        val positions = grid
            .withIndex()
            .flatMap { (i, row) ->
                row.indices
                    .filter { j ->
                        grid[i][j] == null
                    }
                    .map { j ->
                        i to j
                    }
            }
            .shuffled(rng)
            .toMutableList()
        for (i in 1..count) {
            if (positions.isEmpty()) {
                break
            }
            val p = positions.removeLast()
            grid[p.first][p.second] = mergeStrategy.generate()
        }
        return this
    }

    override fun equals(other: Any?) =
        other != null && other is GameState && grid == other.grid

    override fun hashCode() =
        grid.hashCode()
}
