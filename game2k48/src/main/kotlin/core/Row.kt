package core

typealias Row = MutableList<Cell>

fun Row.swipedLeft(mergeStrategy: MergeStrategy): Row {
    val values = filterNotNull()
    val res = arrayListOf<Cell>()
    var i = 0
    while (i < values.size) {
        if (i + 1 >= values.size) {
            res += values[i]
            i += 1
            continue
        }
        mergeStrategy.getNext(values[i], values[i + 1])
            ?.also {
                res += it
                i += 2
            } ?: run {
                res += values[i]
                i += 1
            }
    }
    check(res.size <= size)
    while (res.size < size) {
        res += null
    }
    return res
}
