import Square from "./Square";
import {Code, PlayingField, Position} from './Game'
import React, {ChangeEvent, createRef, KeyboardEvent, MouseEvent, useEffect} from "react";
import Grid from '@mui/material/Grid'

type BoardProps = {
    array: Array<Array<PlayingField>>
    onChange: (event: ChangeEvent<HTMLInputElement>) => void
    onKeyUp: (event: KeyboardEvent<HTMLInputElement>) => void
    current_pos: Position
    change_color_to_code: (event: MouseEvent<HTMLButtonElement>, code: Code, position: Position) => void
}

const Board = ({array, onChange, onKeyUp, current_pos, change_color_to_code}: BoardProps) => {


    let ref = createRef<HTMLInputElement>();
    useEffect(() => {
        if (ref.current) {
            ref.current.focus();
        }
    })

    return (
        <Grid container rowSpacing="9px" width="400px">
            {
                array.map((arr_row, row) =>
                    <Grid container item columns={5} key={`row:${row}`}>
                        {
                            arr_row.map((fieldInfo, column) =>
                                <Grid item key={`row:${row}_col:${column}`} xs={1}>
                                    <Square
                                        key_={`row:${row}_col:${column}_square`}
                                        value={fieldInfo.character}
                                        code={fieldInfo.code}
                                        onChange={(event) => onChange(event)}
                                        onKeyUp={(event) => onKeyUp(event)}
                                        current={current_pos.is(row, column)}
                                        current_ref={ref}
                                        change_color_to_code={change_color_to_code}
                                        self_position={new Position(row, column)}
                                    />
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