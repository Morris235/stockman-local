import React from 'react';
import Button from '@material-ui/core/Button';

// 이 구조는 현재 CounteContainer전용 버튼이 된거 같다. 다른 컴포넌트에서 이용할수 있나? 카운트하는데 이용할순 있다. 
export const CounterButton = ({ onIncrement, onDecrement }) => {
    return (

        <div>
        {/* <h3>count: {value}</h3> */}
        {/* prop으로 함수를 받아올경우 () => onDecrement 이런식으로 받아야함. */}
        <Button type='button' color='primary' variant='contained' onClick={onDecrement}>이전</Button>
        <Button type='button' color='primary' variant='contained' onClick={onIncrement}>다음</Button>
    </div>
    );
}




