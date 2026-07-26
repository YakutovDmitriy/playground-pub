import core.*
import front.*

import kotlinx.browser.document
import kotlinx.browser.window

/**
 * TODO:
 *   + use localStorage
 *   + if swipe does nothing, add no values
 *   - buttons:
 *     - merge strategy
 *     - size of field
 *     - start new game (with storage drop)
 *   - adaptive font size
 */
fun main() {
    val game = GameEngine.runClassic(
        LocalStorage.loadGameState()
    )

    window.onload = {
        document.body?.drawGame(game.state())
    }

    window.onkeyup = { event ->
        console.info("onKeyUp: ${event.key}")

        game.keyToAction()[event.key]
            ?.let { action ->
                action()
            } ?: run {
                console.info("No action found on key ${event.key}")
            }

        document.body?.drawGame(game.state())
        LocalStorage.saveGameState(game.state())
    }
}
