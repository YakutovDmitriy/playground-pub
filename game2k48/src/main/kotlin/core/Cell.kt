package core

typealias Cell = Int?

fun Cell.printable() =
    this?.let { k ->
        var head = k
        var result = ""
        while (head > 999) {
            result += 'k'
            head /= 1000
        }
        "$head$result"
    } ?: ""

fun Cell.htmlClass() =
    this?.let { "cell${if (it > 2048) "Large" else it}" }
        ?: "cellEmpty"
