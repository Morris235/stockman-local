// ducks 패턴
// 액션 타입 정의
export const UPDATE_CURRENT_PAGE = 'count/UPDATE_CURRENT_PAGE';
export const UPDATE_TOTAL_POSTS_COUNT = 'postsCount/UPDATE_TOTAL_POSTS_COUNT';

// action은 어떤 변화가 일어나야 하는지 알려주는 객체.
// 첫번쨰 필드 type은 필수적으로 포함되야 한다.(action이 무엇을 해야하는지 개발자가 임의로 정한 명령어 개념)
// 그 이후의 필드는 개발자가 임의로 추가할 수 있다. 

// 액션 생성자. action 객체를 만든다
// 타입은 액션의 이름과도 같은 존재다. 나중에 리듀서가 액션을 전달 받으면 이 값에 따라서 정의해둔 작업을 하게 된다.

export const updateCurrnetPage = (number) => ({
    type: UPDATE_CURRENT_PAGE,
    number,
});

export const updateTotalPostsCount = (totalCount) => ({
    type: UPDATE_TOTAL_POSTS_COUNT,
    totalCount,
});

// counter의 상태 초기화 : 그냥 state라고 이해하기
export const initialState = {
    pageNumber: 1,
    totalPosts: 0,
};



// UI동작의 로직 코드를 작성하게 된다.
// counter의 리듀서. default 파라미터를 이용하여 state가 undefined로 넘어올 결우 초기 state를 설정해준다.
// default 파라미터란, 함수에 전달된 파라미터 값이 undefined이거나 전달된 값이 없을 때 별도의 예외처리 없이 초기화 설정된 값으로 초기화 해준다. 

// 리듀서 정의
/*
리듀서란?
1.이전 상태와 동작을 받아 새 상태를 리턴한다.
2.반드시 순수 함수여야 한다. 이를테면 데이터베이스 호출이나 HTTP 호출 등 외부의 데이터 구조를 변형하는 호출은 허용되지 않는다.
3.항상 현재 상태를 '읽기 전용'

리듀서가 포함하고 있는 세 가지
1. 할 일을 정의하는 Action(인수는 옵션)
2. 애플리케이션의 모든 데이터를 저장하는 state
3. state와 Action을 받아 새 상태를 리턴하는 Reducer
state를 변경시키지 않고, Object.assign 메소드를 통해 state를 복사하여, 복사한 객체를 수정하여 리턴.(Redux에서 state는 읽기 전용이여야 함)
*/
export default function counter (state = initialState, action) {
    switch(action.type) {
        // action.type에 따라 reducer가 동작하는 부분.
        case UPDATE_CURRENT_PAGE:
            return {
                ...state, // rest 방식이였나? 
                pageNumber: action.number, 
            };
        case UPDATE_TOTAL_POSTS_COUNT:
            return {
                ...state,
                totalPosts: action.totalCount,
            };
            // default case 에서는 원래 state를 리턴한다. 그래야 알 수 없는 동작이 전달되어도 오류가 출력되지 않고 원래 state가 변경되지 않는다.
        default:
            return state;
    }
};