package core

import kotlin.random.Random

interface MergeStrategy {
    fun getFirst(): Int
    fun getNext(first: Int, second: Int): Int?
    fun generate(): Int
}

data class ClassicMS(val rng: Random, val params: Params): MergeStrategy {

    override fun getFirst() = params.first

    override fun getNext(first: Int, second: Int) =
        if (first == second) first * params.multiplier else null

    override fun generate() =
        if (rng.nextInt(8) == 0)
            params.first * params.multiplier
        else
            params.first

    class Params(val first: Int, val multiplier: Int)
}

data class SimpleSumMS(val rng: Random): MergeStrategy {
    override fun getFirst() = 1

    override fun getNext(first: Int, second: Int) = first + second

    override fun generate() = rng.nextInt(1, 2)
}