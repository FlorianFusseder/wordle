import React from 'react'
import {Game} from './components/Game'
import './App.css';
import Box from '@mui/material/Box'

function App() {
    return (
        <Box className="App">
            <link
                rel="stylesheet"
                href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap"
            />
            <link
                rel="stylesheet"
                href="https://fonts.googleapis.com/icon?family=Material+Icons"
            />
            <header className="App-header">
                <Game/>
            </header>
        </Box>
    );
}

export default App;
