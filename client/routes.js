import React from "react";
import {
    Route,
    Link
} from "react-router-dom"

import {App} from "./containers/app"
import {Home} from "./containers/home"
import {SongSingleContainer} from './containers/songs/single'


export default (
    <div>
        <Route exact path="/" component={Home}/>
        <Route path="/songs/:songId" component={SongSingleContainer}/>
    </div>
);

