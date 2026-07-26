package front

import core.GameEngine
import core.SwipeType

fun GameEngine.keyToAction() =
    mapOf(
        "ArrowRight" to { swipe(SwipeType.RIGHT) },
        "ArrowUp"    to { swipe(SwipeType.UP) },
        "ArrowLeft"  to { swipe(SwipeType.LEFT) },
        "ArrowDown"  to { swipe(SwipeType.DOWN) },
        "Backspace"  to this::undo,
        " "          to this::newGame,
    )
