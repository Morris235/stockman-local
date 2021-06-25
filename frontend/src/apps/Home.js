import React, { useEffect, useState }  from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

export default function Home () {

    return (
        <div>
            <h3>화면분할</h3>
        </div>
    )
    // const [compsPosts, setCompPosts] = useState([]);
    // const [loading, setLoading] = useState(false);
    // const [error, setError] = useState(null);

    // // REST-API 서버에서 기업이름과 코드를 비동기로 받아오는 코드
    // const fetchComps = async() => {
    //     try {
    //         setError(null);
    //         setCompPosts(null);
    //         setLoading(true);

    //         const url = `http://localhost:8000/company_state/?page=1&data
    //         cache-control: max-age=60
    //         Cache-Control: no-store`; 
    //         const response = await axios.get(url);

    //         console.log(response.data.results.map(comps => {return comps.year}));
    //         // if (response.data.results.map(comps => {return comps.year}) === '2020'){
    //         //     console.log('ddd');
    //         // }

    //         setCompPosts(response.data.results);
    //     } catch(e) {
    //         setError(e);
    //     }
    //     setLoading(false);
    // };

    // useEffect(() => {
    //     fetchComps();
    // }, []);

    // if (loading) return <div>loading...</div>;
    // if (error) return <div>error.</div>;
    // if (!compsPosts) return null;

    // return (
    //     <div>
    //         <p>updated: 2021-05-23</p>
    //         <table className='table table-hover text-center'>
    //             <thead>
    //                 <tr>
    //                     <th>기업명</th>
    //                     <th>종목코드</th>
    //                     <th>시장</th>
    //                     <th>결산년도</th>
    //                     <th>시가총액</th>
    //                     <th>안정성</th>
    //                     <th>성장성</th>
    //                     <th>가치성</th>
    //                     <th>수익성</th>
    //                     <th>즐겨찾기</th>
    //                 </tr>
    //             </thead>
    //             <tbody>
    //             {compsPosts.map(comps => {
    //                 return (
    //                 <tr key={comps.code}> 
    //                     <td>{comps.company_nm}</td> 
    //                     <td>{comps.code}</td> 
    //                     <td>{comps.mk}</td>
    //                     <td>{comps.year}</td>
    //                     <td>150억</td>
    //                     <td>양호</td>
    //                     <td>양호</td>
    //                     <td>우수</td>
    //                     <td>위험</td>
    //                     <td>*</td>
    //                     </tr>);
    //             })}
    //             </tbody>
    //         </table>
    //     </div>
    // );
}