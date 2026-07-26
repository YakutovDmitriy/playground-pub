package front

import core.GameState

import kotlinx.browser.localStorage
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import org.w3c.dom.get
import org.w3c.dom.set

object LocalStorage {
    private val gameStateKey = "game-state"

    fun loadGameState(): GameState? =
        localStorage[gameStateKey]
            ?.let { GameState(Json.decodeFromString(it)) }

    fun saveGameState(state: GameState) =
        localStorage.set(
            gameStateKey,
            Json.encodeToString(state.grid)
        )
}
