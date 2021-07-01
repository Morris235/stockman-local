import React, { useEffect, useState } from "react";
import { useSelector, shallowEqual } from 'react-redux';
import axios from 'axios';

 export default function Company () {
    const [compsPosts, setCompPosts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);


    // 스토어에서 상태 조회하고 변수에 저장
    const {pageNum} = useSelector(
        state => ({
            pageNum: state.counter.pageNumber,
        }), shallowEqual);
    
        useEffect(() => {
            fetchComps();
        }, [pageNum]);

    


    // REST-API 서버에서 기업이름과 코드를 비동기로 받아오는 코드
    const fetchComps = async() => {
        try {
            setError(null);
            setCompPosts(null);
            setLoading(true);

            const url = `http://localhost:8000/api/company`; 
            const response = await axios.get(url);

            setCompPosts(response.data.results);
        } catch(e) {
            setError(e);
        }
        setLoading(false);
    };



    if (loading) return <div>loading...</div>;
    if (error) return <div>error.</div>;
    if (!compsPosts) return null;
    

    return (
        
        <>
        <div>
        <table>
        <th>
            <tr>
                <td>Code</td>
                <td>Names</td>
                <td>Updated</td>
            </tr>
        </th>

        <tbody>
            {compsPosts.map(comps => { 
                return <tr key={comps.code}><td>{comps.code}</td><td>{comps.company}</td><td>{comps.last_update}</td></tr>
            })}
        </tbody>
        </table>
        </div>

        <div>
            {/* store.getState()로 저장된 state를 가져와, counter.value를 출력한다. 
                store의 state구조 :
                counter: {value:0, diff:1}
                필드명을 가지고, 그 필드명 하위로 state가 구성되어 있다. 필드명은 reducer에서 combineReducers 메소드에서 정의한 키와 동일하다. 
                별도의 key를 설정하지 않았다면 reducer의 이름과 동일한 필드명을 가지게 된다.
                props.store.getState().counter.value
            */}
        <p><b>page : {pageNum}</b></p>
        </div>
        </>
    );
}