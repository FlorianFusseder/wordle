import Board from "./Board";
import Keyboard from "./Keyboard"
import React, {ChangeEvent, KeyboardEvent, MouseEvent, useState} from "react";


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

    submittable(): boolean {
        if (this.row > 5) throw new RangeError(`row not valid, has to be smaller than 6 but was: ${this.row}`)
        return (this.column === 0 && this.row > 0) || this.isEndOfInput()
    }

    is(row: number, column: number): boolean {
        return row === this.row && column === this.column
    }
}

type GameProps = {
    arr: Array<Array<PlayingField>>
    caret: Position
}


export function Game() {

    const pattern: RegExp = new RegExp("^[A-ZÖÄÜ]$", "gm")

    const [gameState, setGameState] = useState<GameProps>({
        arr: Array(6).fill(null).map(() => Array(5).fill({character: "", code: Code._undefined})),
        caret: new Position(0, 0)
    })

    function submitForm() {

        let nonCompleteElement = gameState.arr.slice(0, gameState.caret.row)
            .flat()
            .map((value, index) => ({field: value, index: index}))
            .find((value, index) => (!value.field.code || !value.field.character));

        if (!gameState.caret.submittable() || nonCompleteElement) {
            console.log("Form not submittable like this...")
            if (nonCompleteElement)
                console.log(`${nonCompleteElement.index % 5}`)
        } else {

            const requestOptions = {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: 'Fetch POST Request Example' })
            };
            fetch(`${process.env.API_URL}`, requestOptions)
                .then(response => response.json())
                .then(data => console.log(data) );
        }
    }

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

    function onChange(event: ChangeEvent<HTMLInputElement>) {
        let upperKey: string = event.target.value.toUpperCase()
        if (pattern.test(upperKey) && gameState.caret.canWrite()) {
            write_char(upperKey)
        }
    }

    function onKeyUp(event: KeyboardEvent<HTMLInputElement>) {

        function setColorCode(code: Code) {
            let slice = gameState.arr.slice();
            let uncoded = slice
                .flat()
                .map((value, index) => ({playingField: value, index: index}))
                .find(value => value.playingField.character !== "" && value.playingField.code === Code._undefined)

            if (uncoded) {
                slice[Math.floor(uncoded.index / 5)][uncoded.index % 5] = {
                    character: uncoded.playingField.character,
                    code: code
                };

                setGameState({
                    arr: slice,
                    caret: gameState.caret
                })
            }
        }

        if (event.key === "Backspace") {
            delete_char()
        } else if (event.key === "Enter") {
            submitForm()
        } else if (event.key === "1") {
            setColorCode(Code.green)
        } else if (event.key === "2") {
            setColorCode(Code.yellow)
        } else if (event.key === "3") {
            setColorCode(Code.grey)
        }
    }

    function keyBoardClick(key: string) {
        if (key === "SUBMIT") {
            submitForm()
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
            <Board
                array={gameState.arr}
                onChange={onChange}
                onKeyUp={onKeyUp}
                current_pos={gameState.caret}
                change_color_to_code={(event: MouseEvent<HTMLButtonElement>,
                                       code: Code,
                                       position: Position) => {
                    let slice = gameState.arr.slice();
                    slice[position.row][position.column].code = code
                    setGameState({
                        arr: slice,
                        caret: gameState.caret
                    })
                }}
            />
            <Keyboard onClick={keyBoardClick}/>
        </React.Fragment>
    )
}