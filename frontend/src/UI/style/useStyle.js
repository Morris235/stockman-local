import React from 'react';
import { makeStyle } from '@material-ui/core/styles'
import { Typography } from '@material-ui/core'

const useStyles = makeStyle({
    text: {
        color: "blue",
        backgroundColor: "black",
    },
});

export default function useTestStyle () {
    const classes = useStyles();
    return <Typography className={classes.text}>Test</Typography>
}