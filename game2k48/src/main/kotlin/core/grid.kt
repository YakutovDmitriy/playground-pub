package core

typealias Grid = List<Row>

fun emptyGrid(n: Int, m: Int): Grid =
    List(n) {
        MutableList(m) {
            null
        }
    }

fun Grid.getN(): Int =
    size

fun Grid.getM(): Int =
    if (isEmpty()) 0 else this[0].size

fun Grid.isCorrect(): Boolean =
    getN() > 0 && getM() > 0 && all { it.size == getM() }

fun Grid.checkCorrect(): Unit =
    check(isCorrect()) { toString() }

fun Grid.transposed(): Grid =
    List(getM()) { i ->
        MutableList(getN()) { j ->
            this[j][i]
        }
    }

fun Grid.reflected(): Grid =
    map { it.reversed().toMutableList() }

fun Grid.swipedLeft(mergeStrategy: MergeStrategy): Grid =
    map { it.swipedLeft(mergeStrategy) }

fun Grid.swipedRight(mergeStrategy: MergeStrategy): Grid =
    this.reflected()
        .swipedLeft(mergeStrategy)
        .reflected()

fun Grid.swipedUp(mergeStrategy: MergeStrategy): Grid =
    this.transposed()
        .swipedLeft(mergeStrategy)
        .transposed()

fun Grid.swipedDown(mergeStrategy: MergeStrategy): Grid =
    this.reversed()
        .swipedUp(mergeStrategy)
        .reversed()
