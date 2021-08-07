
// 액션 타입
export const SHOW_COMPANY_INFO = 'company_info/SHOW_COMPANY_INFO';

// counter의 상태 초기화 : 그냥 state라고 이해하기
// 초기상태를 지정할 필요가 있음
export const initialState = {
    code: '005930',
    comp_name: '삼성전자',
    sec_nm: '통신 및 방송 장비 제조업'
};

// 액션 객체 
export const companyInfoActionObject = (code, comp_name, sec_nm) => ({
    type: SHOW_COMPANY_INFO,
    code: code,
    comp_name: comp_name,
    sec_nm: sec_nm,
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
                sec_nm : action.sec_nm,
            };
        // 기존 state 리턴(알수 없는 동작이 전달되어도 오류가 출력되지 않음)
        default:
            return state;
    }
}

