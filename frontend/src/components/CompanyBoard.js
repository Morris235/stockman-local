import React from 'react';
import { BoardInput } from '../UI/atoms/BoardInputForm';
import Company from '../components/CompInfo';
import { GetCompanyTotalPostsCount } from '../components/HTTP';
import Pagination from '../components/Paging';


// 루트 컴포넌트
export default function CompanyBoard () {
    //HTTP 메서드
    GetCompanyTotalPostsCount();

        return (
            <>
        <box clone p={0}>
            <div className="CompanyBoard">
                    <Company />
                    {/* <CounterContainer /> */}
                    <Pagination />
                    <BoardInput />
            </div>
        </box>
            </>
        );
}