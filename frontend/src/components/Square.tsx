import * as React from 'react'
import './Square.css'

interface SquareProps {
    value: string,
    onClick: () => void
    current: number
}

const Square = ({value, onClick, current}: SquareProps) => (
    <button
        className={(current) ? "active square" : "square"}
        onClick={onClick}>
        {value}
    </button>
)


export default Square