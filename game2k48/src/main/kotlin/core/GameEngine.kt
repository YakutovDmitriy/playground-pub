package core

import kotlinx.html.currentTimeMillis
import kotlin.random.Random

class GameEngine private constructor(
    private val params: GameParams,
    private val rng: Random,
    initialState: GameState
) {
    private val stack = ArrayDeque(listOf(initialState))

    fun state() =
        stack.last()

    fun swipe(swipeType: SwipeType) {
        val newState = state()
            .copy()
            .swipe(swipeType, params.ms)
        if (state() != newState) {
            changeState(newState.tryAddRandomCell(rng, params.ms, 1))
        }
    }

    fun undo() {
        if (stack.size > 1) {
            stack.removeLast()
        }
    }

    fun newGame() {
        changeState(genClassicInitialState())
    }

    private fun changeState(state: GameState) {
        check(state.grid.getN() == params.n)
        check(state.grid.getM() == params.m)
        stack += state
        if (stack.size > params.stackCapacity) {
            stack.removeFirst()
        }
    }

    companion object {
        private val rng = Random(currentTimeMillis())
        private val classicParams = GameParams(
            n = 4,
            m = 4,
            ms = ClassicMS(rng, ClassicMS.Params(2, 2)),
            stackCapacity = 100,
        )

        fun runClassic(initialState: GameState?) =
            GameEngine(classicParams, rng, initialState ?: genClassicInitialState())

        private fun genClassicInitialState() =
            GameState.generateInitial(classicParams, rng)
    }
}
