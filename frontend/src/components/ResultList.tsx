import "./ResultList.css"
import * as React from 'react';
import Box from '@mui/material/Box';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import ListSubheader from '@mui/material/ListSubheader';

type ResultListProps = {
    list: Array<string>
}


export const ResultList = ({list}: ResultListProps) => {
    return (
        <Box className="result-list">
            <nav aria-label="wordlist">
                <List dense={true} subheader={<li/>}>
                    <ListSubheader sx={{bgcolor: "#94999e"}}>Results</ListSubheader>
                    {
                        list.map((word, index) => (
                            <ListItem key={index} disablePadding>
                                <ListItemButton>
                                    <ListItemText primary={index + 1 + ". " + word}/>
                                </ListItemButton>
                            </ListItem>
                        ))
                    }
                </List>
            </nav>
        </Box>
    )
}