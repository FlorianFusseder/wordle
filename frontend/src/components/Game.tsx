import Board from "./Board";
import Keyboard from "./Keyboard"
import React, {useState} from "react";
import './Game.css'

type GameProps = {
    arr: Array<[string, string | null]>
    current: number
}


function Game() {

    const [props, setProps] = useState<GameProps>({
        arr: new Array(5 * 6).fill(["", null]),
        current: 0,
    })

    function selectCode(index: number, event: any) {
        let slice = props.arr.slice();
        slice[index] = [event.target.value, null]
        setProps({
            arr: slice,
            current: props.current + 1
        })
    }

    function keyBoardClick(key: string) {
        if (key === "submit") {

        } else {
            let slice = props.arr.slice();
            if (key === "delete") {
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
                <Board array={props.arr} onChange={selectCode} current={props.current}/>
            </div>
            <div className="game-keyboard">
                <Keyboard onClick={keyBoardClick}/>
            </div>
        </div>
    )
}


export default Game
export type {GameProps}