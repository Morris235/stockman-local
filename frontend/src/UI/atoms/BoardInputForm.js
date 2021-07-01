import React, { useState } from 'react';
// import UI from './styles/Material_ui';


// 게시판 검색어 입력 폼
export function BoardInput () {
    // 상태 초기화
    const [text, setValue] = useState('');

    //값이 변경됐을 때
    const onChange = (e) => { 
        const newText = e.target.value;
        setValue(newText); // setStatus 값의 변동이 있을 때 사용하는 메서드
        e.preventDefault();
    }

    // 검색 내용 제출
    const doSubmit = (e) => {
        window.alert('검색:' + text)
        setValue('');
        e.preventDefault(); // from 안에 있는 input등의 전송하는 동작을 중단한다.
    }

        return (
            <div style={{float: 'left', marginTop: '10px'}}>
               <form onSubmit={doSubmit}>

                   <input type='text'
                   name='onChange'
                   value={text}
                   onChange={onChange}
                   placeholder='종목의 이름 또는 코드명' />

                   <button variant='contained' color='primary' type='submit'>검색</button>
               </form>
            </div>
        );
}
