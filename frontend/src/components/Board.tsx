import Square from "./Square";
import {Position, PlayingField} from './Game'
import React, {ChangeEvent, KeyboardEvent, createRef, useEffect} from "react";
import Grid from '@mui/material/Grid'

type BoardProps = {
    array: Array<Array<PlayingField>>
    onChange: (event: ChangeEvent<HTMLInputElement>) => void
    onKeyUp: (event: KeyboardEvent<HTMLInputElement>) => void
    current_pos: Position
}

const Board = ({array, onChange, onKeyUp, current_pos}: BoardProps) => {


    let ref = createRef<HTMLInputElement>();
    useEffect(() => {
        if (ref.current) {
            ref.current.focus();
        }
    })

    return (
        <Grid container spacing={1} marginBottom={5}>
            {
                array.map((arr_row, row) =>
                    <Grid container item columns={5} spacing={.5} justifyContent="center" key={`row:${row}`}>
                        {
                            arr_row.map((fieldInfo, column) =>
                                <Grid item key={`row:${row}_col:${column}`}>
                                    <Square
                                        key_={`row:${row}_col:${column}_square`}
                                        value={fieldInfo.character}
                                        code={fieldInfo.code}
                                        onChange={(event) => onChange(event)}
                                        onKeyUp={(event) => onKeyUp(event)}
                                        current={current_pos.is(row, column)}
                                        current_ref={ref}/>
                                </Grid>
                            )
                        }
                    </Grid>
                )
            }
        </Grid>
    )
}


export default Board