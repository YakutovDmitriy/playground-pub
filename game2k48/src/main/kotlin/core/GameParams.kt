package core

data class GameParams(
    val n: Int,
    val m: Int,
    val ms: MergeStrategy,
    val stackCapacity: Int,
) {
    init {
        check(n > 0)
        check(m > 0)
        check(stackCapacity > 0)
    }
}
