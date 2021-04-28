// combineReducers를 사용해 보기 위해 만들어진 실험용 extra reducer다.
export default function extra (state =  { value: 'this_is_extra_reducer' }, action) {
    switch(action.type) {
        default:
            return state;
    }
}