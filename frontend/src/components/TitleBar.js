import React from "react";

export default function TitelBar () {
    // 코스피, 코스닥, 금리, VIX 지수를 실시간 확인할수 있도록 기능을 넣어야한다.
    return (
        <nav class="navbar navbar-expand navbar-dark bg-dark">
            <div class="container">
                <a href="#home" class="navbar-brand">STOCKMAN</a>
                <div class="me-auto navbar-nav">
                    <a href="#home" data-rb-event-key="#home" class="nav-link active">Home</a>
                    <a href="#features" data-rb-event-key="#features" class="nav-link">Features</a>
                    <a href="#pricing" data-rb-event-key="#pricing" class="nav-link">Pricing</a>
                </div>
            </div>
        </nav>
    )

}