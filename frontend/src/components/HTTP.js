/**
 * HTTP 통신 담당 메서드, 필요하다면 상태값 업데이트까지 해준다.
 * 각 컴포넌트마다 필요한 HTTP 메서드를 정의 

 * 주의 : 
 * 아직은 간단한 구조의 컴포넌트에서만 사용가능, 간단한 HTTP 요청만 가능함
 * Hooks를 useEffect에서 사용할 수 없음
 * Hooks를 try문 블록에서 사용할 수 없음
 * EX) 
 *  1. A 앱에서 HTTP 컴포넌트의 P 메서드 호출
 *  2. HTTP 컴포넌트의 P메서드가 HTTP 통신을하고 상태 값을 디스패치
 *  3. A앱에 속한 컴포넌트에서 해당 상태값을 참조
 * 
*/
import { useState } from 'react';
import axios from 'axios';
import { useDispatch } from 'react-redux';
import { updateTotalPostsCount } from '../modules/Counter';
    

/* GET 메서드 집합 */

export const GetCompanyTotalPostsCount = async() => {
    const dispatch = useDispatch();
    const [totalPostsCount, setTotalPostsCount] = useState(0);

    try{
        const url = `http://localhost:8000/api/company`;
        const response = await axios.get(url);
        setTotalPostsCount(response.data.count);
    } catch(e){
            console.log(e);
        }
    dispatch(updateTotalPostsCount(totalPostsCount));
    };


/* 무한히 많은 GET을 요청하는 바람에 브라우저와 서버가 멈추는 현상이 있음 */
// export const GetCompanyNamesPage = async() => {
//     const {pageNum} = useSelector(
//         state => ({
//             pageNum: state.counter.pageNumber,
//         }), shallowEqual);

//     const [companyNames, setCompanyNames] = useState();

//     
//     try{
//         // 리덕스의 pageNumber의 상태값을 참조하여 HTTP GET 
//         const url = `http://localhost:8000/company/?page=1&data`; 
//         const response = await axios.get(url);
//         setCompanyNames(response);
//     } catch(e){
//         console.log(e);
//     }
//     console.log(companyNames);
//     console.log('excute!');
//     return companyNames;
// };