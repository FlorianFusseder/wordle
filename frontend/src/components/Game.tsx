import Board from "./Board";
import Keyboard from "./Keyboard"
import React, {ChangeEvent, KeyboardEvent, useState} from "react";
import './Game.css'

type GameProps = {
    arr: Array<[string, string | null]>
    current: number
}


function Game() {

    const pattern: RegExp = new RegExp("^[A-ZÖÄÜ]$", "gm")

    const [props, setProps] = useState<GameProps>({
        arr: new Array(5 * 6).fill(["", null]),
        current: 0,
    })

    function submitForm() {
        if (props.current === 0 || props.current % 5 !== 0) {
            console.log("Form not submittable like this")
        } else {
            console.log("submit")
        }
    }

    function onChange(index: number, event: ChangeEvent<HTMLInputElement>) {
        let upperKey: string = event.target.value.toUpperCase()
        if (pattern.test(upperKey)) {
            let slice = props.arr.slice();
            slice[index] = [upperKey, null]
            setProps({
                arr: slice,
                current: props.current + 1
            })
        } else {
            console.log("onChange ignored: " + event.target.value)
        }
    }

    function onKeyUp(index: number, event: KeyboardEvent<HTMLInputElement>) {
        if (event.key === "Backspace") {
            let slice = props.arr.slice();
            slice[index - 1] = ["", null]
            setProps({
                arr: slice,
                current: props.current - 1
            })
        } else if (event.key === "Enter") {
            submitForm()
        }
    }

    function keyBoardClick(key: string) {
        if (key === "SUBMIT") {
            submitForm()
        } else {
            let slice = props.arr.slice();
            if (key === "DELETE") {
                slice[props.current - 1] = ["", null]
                setProps({
                    arr: slice,
                    current: props.current - 1
                })
            } else {
                slice[props.current] = [key, null]
                setProps({
                    arr: slice,
                    current: props.current + 1
                })
            }

        }
    }

    return (
        <div className="game-board">
            <div className="word-list">
                <Board
                    array={props.arr}
                    onChange={onChange}
                    onKeyUp={onKeyUp}
                    current={props.current}/>
            </div>
            <div className="game-keyboard">
                <Keyboard onClick={keyBoardClick}/>
            </div>
        </div>
    )
}


export default Game
export type {GameProps}