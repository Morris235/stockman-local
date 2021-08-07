/*특정 기능을 구현하기위하여 필요한 액션과, 액션생성함수와, 초깃값과, 리듀서함수가 들어있다.
이를 모듈이라고 부른다. */
import { combineReducers } from 'redux';  // combineReducers는 reducer가 여러개 있다면 하나로 합칠 때 사용되는 redux 내장 메소드다.
import counter from './Counter';
import searchReducer from './SearchReducer';

// combineReducers의 사용예: 작성한 reducer를 하나로 합쳐준다.
// reducer를 여러개로 분리하여 작성할 땐, 서로 직접적인 관계가 없어야 한다.
export const rootReducer = combineReducers ({                    // 타입스크립트 적용 : export default를 export로 바꾸고
    counter: counter,
    searchReducer: searchReducer,
});

/*
reducer에 다른 key를 주고 싶다면 이렇게 사용하면 된다.
const defaultReducer = combineReducers ({
    a: counter,
    b: etc
});
*/

// reducer를 export한다.
// type 키워드를 써서 RootState라는 타입을 rootReducer로 만든건가?
// export type RootState = ReturnType<typeof rootReducer>          
