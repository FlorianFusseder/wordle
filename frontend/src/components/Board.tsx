import Square from "./Square";
import React from "react";

type BoardProps = {
    array: Array<[string, string|null]>
    onChange: (index: number, event: any) => void
    current: number
}

const Board = ({array, onChange, current}: BoardProps) => {

    function renderSquare(index: number) {
        return <Square value={array[index][0]} code={array[index][1]} onChange={(event) => onChange(index, event)} current={current === index}/>
    }

    function renderRow(index: number) {
        return (
            <div className="board-row">
                {renderSquare(index * 5)}
                {renderSquare(index * 5 + 1)}
                {renderSquare(index * 5 + 2)}
                {renderSquare(index * 5 + 3)}
                {renderSquare(index * 5 + 4)}
            </div>
        )
    }

    return (
        <div className="board">
            {renderRow(0)}
            {renderRow(1)}
            {renderRow(2)}
            {renderRow(3)}
            {renderRow(4)}
            {renderRow(5)}
        </div>
    )
}


export default Board