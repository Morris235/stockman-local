import { initialState } from "./Counter";

// 액션 타입
export const SHOW_COMPANY_INFO = 'company/SHOW_COMPANY_INFO';

// 액션 객체 
export const companyInfoActionObject = (code, comp_name) => ({
    type: SHOW_COMPANY_INFO,
    code,
    comp_name,
});

// 리듀서
export default function companyInfoReducer (state = initialState, action) {
    // action.type에 따라 reducer 동작.
    switch(action.type) {
        case SHOW_COMPANY_INFO:
            return {
                ...state, // rest 방식.
                code: action.code,
                comp_name: action.comp_name,
            };
        // 기존 state 리턴(알수 없는 동작이 전달되어도 오류가 출력되지 않음)
        default:
            return state;
    }
}

