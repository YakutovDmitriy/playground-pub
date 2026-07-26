package front

import core.GameState
import core.htmlClass
import core.printable
import kotlinx.html.TagConsumer
import kotlinx.html.dom.append
import kotlinx.html.table
import kotlinx.html.td
import kotlinx.html.tr
import org.w3c.dom.Element
import org.w3c.dom.HTMLElement
import org.w3c.dom.asList

private object Consts {
    val TABLE_CLASS = "main-table"
    val TD_CLASS = "main-cell"
    val TD_INNER_CLASS = "main-inner-cell"
}

fun TagConsumer<HTMLElement>.gameStateToTable(state: GameState) {
    table(Consts.TABLE_CLASS) {
        state.grid.map { row ->
            tr {
                row.map { cell ->
                    td("${Consts.TD_CLASS} ${cell.htmlClass()}") {
                        +cell.printable()
                    }
                }
            }
        }
    }
}

fun Element.drawGame(state: GameState) {
    getElementsByClassName(Consts.TABLE_CLASS)
        .asList()
        .map {
            this.removeChild(it)
        }

    append {
        gameStateToTable(state)
    }
}
