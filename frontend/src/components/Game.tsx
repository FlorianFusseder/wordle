import Board from "./Board";
import Keyboard from "./Keyboard"
import React, {ChangeEvent, KeyboardEvent, MouseEvent, useState} from "react";
import {ResultList} from "./ResultList";
import Stack from "@mui/material/Stack";
import Alert from '@mui/material/Alert';

export enum Code {
    green = "t",
    yellow = "c",
    grey = "f",
    _undefined = ""
}

export type PlayingField = {
    character: string,
    code: Code
}

export class Position {
    readonly row: number
    readonly column: number

    constructor(row: number, column: number) {
        if ((row !== undefined && column !== undefined) && (row <= 5 && row >= 0) && (column >= 0 && column <= 4)) {
            this.column = column
            this.row = row
        } else
            throw new RangeError(`Position Out of bounds: row: ${row} column ${column}`)
    }

    getNext(): Position {
        let nextPos: Position
        if (this.column < 4 && this.row <= 5)
            nextPos = new Position(this.row, this.column + 1)
        else if (this.column === 4 && this.row < 5)
            nextPos = new Position(this.row + 1, 0)
        else if (this.isEndOfInput())
            nextPos = this
        else {
            throw new RangeError(`Position Out of bounds: row: ${this.row} column ${this.column}`)
        }
        return nextPos
    }

    getPrevious(): Position {
        let previousPos: Position
        if (this.column <= 4 && this.column > 0 && this.row < 6)
            previousPos = new Position(this.row, this.column - 1)
        else if (this.column === 0 && this.row <= 5 && this.row > 0)
            previousPos = new Position(this.row - 1, 4)
        else if (this.column === 0 && this.row === 0)
            previousPos = new Position(0, 0)
        else {
            throw new RangeError(`Position Out of bounds: row: ${this.row} column ${this.column}`)
        }
        return previousPos
    }

    canDelete(): boolean {
        return this.row > 0 || this.column > 0
    }

    canWrite(): boolean {
        return this.row <= 5 && this.column <= 4
    }

    isEndOfInput(): boolean {
        return this.row === 5 && this.column === 4
    }

    is(row: number, column: number): boolean {
        return row === this.row && column === this.column
    }
}

type GameProps = {
    arr: Array<Array<PlayingField>>
    caret: Position
}

type resultList = {
    header: string
    results: Array<string>
    filled_row_number: number
}


export function Game() {

    const pattern: RegExp = new RegExp("^[A-ZÖÄÜ]$", "gm")

    const startResultState = {
        results: ["asien", "stier", "steak", "saite", "eiter", "senat", "eisen", "arsen", "liane", "aster"],
        header: "Startwörter:",
        filled_row_number: -1,
    }

    const startGameState = {
        arr: Array(6).fill(null).map(() => Array(5).fill({character: "", code: Code._undefined})),
        caret: new Position(0, 0)
    }

    const [gameState, setGameState] = useState<GameProps>(startGameState)

    const [resultState, setResultState] = useState<resultList>(startResultState);

    function delete_char() {
        if (gameState.caret.canDelete()) {
            let slice = gameState.arr.slice();
            let new_pos: Position
            if (gameState.caret.isEndOfInput() && slice[5][4].character !== "") {
                new_pos = gameState.caret
            } else {
                new_pos = gameState.caret.getPrevious()
            }
            slice[new_pos.row][new_pos.column] = {character: "", code: Code._undefined}
            setGameState({
                arr: slice,
                caret: new_pos
            })
            if (new_pos.is(0, 0)) {
                setResultState(startResultState)
            }
        }
    }

    function write_char(key: string) {
        if (gameState.caret.canWrite()) {
            let slice = gameState.arr.slice();
            slice[gameState.caret.row][gameState.caret.column] = {character: key, code: Code._undefined}
            setGameState({
                arr: slice,
                caret: gameState.caret.getNext()
            })
        }

    }

    function onListClick(word: string) {
        let slice = gameState.arr.slice();

        let playingField = slice.flat()
            .flat()
            .map((value, index) => ({field_: value, index_: index}))
            .find(value => value.field_.character === "");

        if (playingField) {
            let i = Math.floor(playingField.index_ / 5)

            for (let j = 0; j < 5; j++) {

                const char = word.at(j);
                if (char)
                    slice[i][j] = {
                        character: char.toUpperCase(),
                        code: Code._undefined
                    }
                else
                    throw new Error("Word is not 5 long")

            }

            setGameState({
                arr: slice,
                caret: new Position((i !== 5) ? i + 1 : i, (i !== 5) ? 0 : 4)
            })


        } else {
            <Alert severity="error">This is an error alert — check it out!</Alert>
        }

    }

    function onChange(event: ChangeEvent<HTMLInputElement>) {
        let upperKey: string = event.target.value.toUpperCase()
        if (pattern.test(upperKey) && gameState.caret.canWrite()) {
            write_char(upperKey)
        }
    }

    /**
     * Sets gamestate for colors, and submits if possible
     * @param slice new slice
     * @param row complete row number to determine if a submit should be triggered
     */
    function changeColorToCode(slice: Array<Array<PlayingField>>) {
        function submit(): number | undefined {
            let rowIndex = slice.slice()
                .reverse()
                .findIndex(row => row.every(column => column.code && column.character));
            rowIndex = (rowIndex !== -1) ? ((gameState.arr.length - 1) - rowIndex) : rowIndex

            let lastRowCompletelyFilledRowIndexHasChanged = rowIndex !== resultState.filled_row_number;
            let playingFieldDataFilledUntilLastRow = gameState.arr.slice(0, rowIndex)
                .every(row => row.every(column => column.code !== Code._undefined && column.character));
            if (playingFieldDataFilledUntilLastRow) {
                if (lastRowCompletelyFilledRowIndexHasChanged || (!lastRowCompletelyFilledRowIndexHasChanged &&
                    gameState.arr.some((row, rowIndex) => row.some((column, columnIndex) => (column.code !== slice[rowIndex][columnIndex].code))))
                )
                    return rowIndex
            }
        }

        const rowIndex = submit()
        // GameState HAS to be set after submit check
        if (rowIndex !== undefined) {
            console.log("Submit that shit")
            const uri: string | undefined = process.env.REACT_APP_API_URL
            if (uri) {
                let objects = slice.slice(0, rowIndex + 1).map(value => {
                    let word: string = value.map(value1 => value1.character).join("")
                    let code: string = value.map(value1 => value1.code).join("")
                    return [[word], code]
                })

                const postBody: object = Object.fromEntries(objects)
                console.log(postBody)
                const requestOptions = {
                    method: 'POST',
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(postBody)
                };
                fetch(uri, requestOptions)
                    .then(response => response.json())
                    .then(data => {
                        setResultState({
                            results: data.matches,
                            header: "Ergebnisse:",
                            filled_row_number: rowIndex,
                        })
                    })
                    .catch(reason => console.log(reason))
            } else {
                throw new Error(`Could not read required env "REACT_APP_API_URL"`)
            }
        }
        setGameState(prevState => ({
            ...prevState,
            arr: slice,
        }))
    }

    function onKeyUp(event: KeyboardEvent<HTMLInputElement>) {

        function setColorCode(code: Code) {
            let slice = gameState.arr.slice();
            let uncoded = slice
                .flat()
                .map((value, index) => ({playingField: value, index: index}))
                .find(value => value.playingField.character !== "" && value.playingField.code === Code._undefined)

            if (uncoded) {
                let row = Math.floor(uncoded.index / 5);
                slice[row][uncoded.index % 5] = {
                    character: uncoded.playingField.character,
                    code: code
                };
                changeColorToCode(slice)
            }
        }

        if (event.key === "Backspace") {
            delete_char()
        } else if (event.key === "1") {
            setColorCode(Code.green)
        } else if (event.key === "2") {
            setColorCode(Code.yellow)
        } else if (event.key === "3") {
            setColorCode(Code.grey)
        }
    }

    function keyBoardClick(key: string) {
        if (key === "CLEAR ALL") {
            setGameState(startGameState)
            setResultState(startResultState)
        } else if (key === "CLEAR ROW") {
            if (!gameState.caret.is(0, 0)) {
                let slice = gameState.arr.slice();
                const rowToClear = (gameState.caret.column > 0) ? gameState.caret.row : gameState.caret.row - 1
                if (rowToClear) {
                    slice[rowToClear] = Array(5).fill({
                        character: "",
                        code: Code._undefined
                    })
                    changeColorToCode(slice)
                    setGameState(prevState => ({
                        ...prevState,
                        caret: new Position(rowToClear, 0)
                    }))
                } else {
                    setGameState(startGameState)
                    setResultState(startResultState)
                }
            }
        } else {
            if (key === "DELETE") {
                delete_char();
            } else {
                write_char(key);
            }
        }
    }

    return (
        <React.Fragment>
            <Stack direction="row" marginBottom="30px">
                <Board
                    array={gameState.arr}
                    onChange={onChange}
                    onKeyUp={onKeyUp}
                    current_pos={gameState.caret}
                    change_color_to_code={(event: MouseEvent<HTMLButtonElement>, code: Code, position: Position) => {
                        let gameSlice = gameState.arr.slice();
                        let rowSlice = gameSlice[position.row].slice()
                        rowSlice[position.column] = {
                            character: rowSlice[position.column].character,
                            code: code
                        }
                        gameSlice[position.row] = rowSlice
                        changeColorToCode(gameSlice);
                    }}
                />
                <ResultList list={resultState.results.slice()} header={resultState.header} onListClick={onListClick}/>
            </Stack>
            <Keyboard onClick={keyBoardClick}/>
        </React.Fragment>
    )
}