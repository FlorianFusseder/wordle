import Square from "./Square";
import React, {ChangeEvent, KeyboardEvent, createRef, useEffect} from "react";
import Grid from '@mui/material/Grid'

type BoardProps = {
    array: Array<[string, string | null]>
    onChange: (index: number, event: ChangeEvent<HTMLInputElement>) => void
    onKeyUp: (index: number, event: KeyboardEvent<HTMLInputElement>) => void
    current: number
}

const Board = ({array, onChange, onKeyUp, current}: BoardProps) => {


    let ref = createRef<HTMLInputElement>();
    useEffect(() => {
        if (ref.current) {
            ref.current.focus();
        }
    })

    function renderSquare(index: number) {
        return (
            <Grid item>
                <Square
                    value={array[index][0]}
                    code={array[index][1]}
                    onChange={(event) => onChange(index, event)}
                    onKeyUp={(event) => onKeyUp(index, event)}
                    current={current === index}
                    current_ref={ref}/>
            </Grid>
        )

    }

    function renderRow(index: number) {
        return (
            <Grid container item columns={5} spacing={.5} justifyContent="center">
                {renderSquare(index * 5)}
                {renderSquare(index * 5 + 1)}
                {renderSquare(index * 5 + 2)}
                {renderSquare(index * 5 + 3)}
                {renderSquare(index * 5 + 4)}
            </Grid>

        )
    }

    return (
        <Grid container spacing={1} marginBottom={5}>
            {renderRow(0)}
            {renderRow(1)}
            {renderRow(2)}
            {renderRow(3)}
            {renderRow(4)}
            {renderRow(5)}
        </Grid>
    )
}


export default Board