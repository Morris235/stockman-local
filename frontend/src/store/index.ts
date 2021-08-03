// 스토어

// 애플리케이션 하나당 하나의 스토어만 정의해야한다.
import { createStore } from 'redux';

export default function create (reducer:any, devTools:any) {
    return createStore(reducer, devTools);
}

