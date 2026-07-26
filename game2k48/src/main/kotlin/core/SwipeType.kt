package core

enum class SwipeType(val horizontal: Boolean, val swipe: (Grid, MergeStrategy) -> Grid) {
    RIGHT(true, Grid::swipedRight),
    UP(false, Grid::swipedUp),
    LEFT(true, Grid::swipedLeft),
    DOWN(false, Grid::swipedDown);

    fun getPaired() =
        when (this) {
            RIGHT -> DOWN
            UP -> LEFT
            LEFT -> UP
            DOWN -> RIGHT
        }
}
