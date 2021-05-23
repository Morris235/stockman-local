
/** @jsxImportSource @emotion/react */
// 위의 주석 삭제해 버리고 싶다. 
import { useState, useRef } from "react";
// import axios from 'axios';

import { Button, makeStyles } from '@material-ui/core';
import { useDispatch, useSelector, shallowEqual } from 'react-redux';
import { updateCurrnetPage } from '../modules/Counter';
import { css } from '@emotion/react';



export default function Pagination () {

    const {totalPostsCount} = useSelector(
        state => ({
            totalPostsCount: state.counter.totalPosts,
        }), shallowEqual);

    const dispatch = useDispatch();
    const [postsPerPage] = useState(10); 
    const [currentPageNumber, setCurrentPageNumber] = useState(1); // 현재 사용자가 보고 있는 페이지 : 1번
    const [target, setTarget] = useState();
    const pageRef = useRef(0);

    // DOM에 함수를 전달할 때 객체 자체를 전달하면(괄호없이) event객체를 함수에 인자로 전달할수 있다. 
    const targetTest = (e) => { // 이벤트 풀링 릴리즈 17부터 이벤트 풀링은 제거됨?
        const value = e.currentTarget.id;
        setTarget(value);
    };

    /* 전체 페이지 배열을 표시할 게시물수(10개) 단위로 나누기, ceil로 나머지수 올림 */ 
    const totalPageCount = Math.ceil(totalPostsCount / postsPerPage); // 242

    /* Array.from()으로 길이가 totalCount, 값이 (1~totalCount+1)인 배열 생성 */
    const pagesArray = Array.from({length: totalPageCount}, (v, i) => i+1); //1~242


/* emotion CSS */ 
// 머티리얼 UI 버튼에는 적용 안되고 그 안에 텍스트는 적용됨
const buttonText = css`
font-size: 14px;
&:hover {
    color: blue;
}
`;

/* Mui theme */
const useStyles = makeStyles(theme => ({
    pageBtn : {
        backgroundColor : '',
        borderRadius : '20px',
        '&:hover': {
            backgroundColor : '#B8DFF8',
        },
    },
    startEndBtn : {
        backgroundColor : '',
        '&:hover': {
            backgroundColor : '#B8DFF8'
        }
    },
    div : {
        marginTop : '10px',
    },
    clickedBtn : {
        backgroundColor : 'red',
    },
}));
const classes = useStyles();



    /* 페이지 넘버 클릭 특정 함수 */
    const OnClicked = (pageNum) => {
        setCurrentPageNumber(pageNum);
        dispatch(updateCurrnetPage(pageNum));
    };

    /* 처음, 끝 버튼 클릭 함수 */
    const OnStartEndClicked = (assignPageNum) => {
        dispatch(updateCurrnetPage(assignPageNum));
        setCurrentPageNumber(assignPageNum);
    };




    /*왜 코드를, 기능을 이렇게 작성했는지 이유와 근거를 써놓으면 나중에 이 코드에 대해 누군가에게 설명할 때 딴소리나 개소리를 안할 수 있다.*/
    /**
     * inputCurrPageNum : currentPageNumber (useState(1))
     * pageArr : pagesArray (길이가 totalCount, 값이 (1~totalCount+1)인 배열. 전체 페이지수의 값이 담긴 배열)
     * startIndex : currPageNum의 값으로부터 -6인 숫자
     * endIndex : currPageNum의 값으로부터 +5인 숫자 
     * ex) currPageNum = 10, startIndex = 4(값:5), endIndex = 15(값:16) 따라서 pageArr.slice(4, 15) 값이 5~15까지인 배열을 만들어 리턴한다.
     * 새로운 배열을 만들어 리턴했기 때문에 인덱스는 항상 0~9다.
     * 
    */
    const createSlicedArray = (inputCurrPageNum, pageArr) => { 
        let [start, end] = [];
        let startIndex = (inputCurrPageNum - 6);
        let endIndex = (inputCurrPageNum + 5);
        // console.log("paging's currPageNum: "+currPageNum);

        // 새로고침 눌렀을 때 클릭했던 페이지에 그대로 머물게 해야함 : useRef로 새로고침 감지? 감지되면 기존 페이지 인덱스, 선택 페이지 정보 남기기
        // useRef 를 사용하면?

        // outOfIndexBend 예외처리 
        if(startIndex < 0) {
            startIndex = 0;
        } else if (endIndex > totalPageCount) {
            endIndex = totalPageCount;
        }
        [start, end] = [startIndex, endIndex];

        // 처음 10페이지를 표시: 10페이지를 선택하면 15페이지까지, 이전 5페이지까지 보여준다. 1~9페이지까지는 동적 변동 없다.
        if(currentPageNumber < 10){
            return pageArr.slice(0, 10); // 10페이지 미만으로 선택할시 페이징 변화 없음
        }else {
            return pageArr.slice(start, end);; // 10페이지 이상으로 선택할시에 동적으로 11개씩 페이징
        }
    };

 
        /* 페이징 UI 처리 하기 */
        // <div style={{float:'left'}}>
        // css 적용: className={classes.primary}
        return (
            <div className={classes.div}>
                {/* <button id='asd' onClick={targetTest}>target test</button> */}
                <Button className={classes.startEndBtn} onClick={() => OnStartEndClicked(1)}>처음</Button>
                {/* <button id='sss'>test button</button> */}
                {
                // OnClicked() 메서드에서 업데이트한 currentPageNumber를 Paging() 메서드에 보내서 페이징 배열을 재생성한다.
                createSlicedArray(currentPageNumber, pagesArray).map((currentValue, index, array) => {
                    // {console.log('HTML id: '+currentValue);}
                    return ( 
                        <Button
                        id={currentValue}
                        ref={pageRef}
                        variant='text'
                        key={index} 
                        className={classes.pageBtn}
                        // onClicked() 메서드는 클릭한 인덱스의 값을 setCurrentPageNumber(currentValue)하여 currentPageNumber를 업데이트 시킨다.
                        // 값을 dispatch한다.
                        onClick= { () => OnClicked(currentValue) }> 
                        {currentValue} 
                        </Button> 
                );
                })}
                <Button className={classes.startEndBtn} onClick={() => OnStartEndClicked(totalPageCount)}>끝</Button>
            </div>
        );
}