// function ask(question, yes, no) {
//    if (confirm(question)) yes()
//    else no();
//  }
 
//  ask(
//    "동의하십니까?",
//    function() { alert("동의하셨습니다."); },
//    function() { alert("취소 버튼을 누르셨습니다."); }
//  );

// ask("동의하십니까?",
// () => alert("동의하셨습니다."),
// () => alert("취소 버튼을 누르셨습니다.")
// );

// // 함수선언식과 동일하게 선언과 동시에 메모리에 올라가므로 코드상 어디에서든 호출할 수 있다.
// let ask = (question,yes,no) => confirm(question) ? yes() : no();


let user = {};

user = {
   name: "morris",
   age: 31,
};


user["dev morris"] = 777;

for(let key in user){
   alert(key);
}

alert(`${user.name} ${user.age} ${user['name']}`);











// let x = prompt('x',''), n = prompt('n', '');

// function pow(x, n) {
//    let tmp = 1;
//    for (let i = 1; i<=n; i++){
//       tmp *= x;
//    }
//    return tmp;
// }


// let x = prompt('x',''), n = prompt('n', '');

// function pow(x,n){
//    return x ** n;
// }
// alert(pow(x,n));

// alert('javascript alert! from anathor module');










// let ID = prompt('아이디 입력:', '');                  
// let PWS = ''; 

// if(ID == 'Admin') 
// {
//     PWS = prompt('비밀번호 입력:', '');

//     if(PWS == 'TheMaster') 
//      {
//         alert('환영합니다.'); 
//      } 
//     else if(PWS == '' || PWS == undefined) 
//      { 
//         alert('취소 되었습니다.'); 
//      } 
//     else 
//      { 
//         alert('인증에 실패했습니다.'); 
//      }
// } else if(ID != 'Admin') 
//     { if (ID == '' || ID == undefined)
//       {
//         alert('취소되었습니다.'); 
//       }
//       else alert('알 수 없는 유저 입니다.'); 
//     }      








// let range = prompt('범위 입력:',''); 

// pri:for (let i = 2; i<range; i++) { 
//    for (let j = 2; j<i; j++){
//       if(i % j == 0) continue pri;
//    }
//    alert(i);
// }






// let range = prompt('범위 입력:',''); 

// pri:for (let i = 1; i<range; i++) { 
//    if(i % 2 == 0 || i % 3 == 0 || i % 5 == 0) continue;
//    alert(i);
// }








// let age = prompt('나이 입력','');

// function checkAge(age) {
//    if (age >= 18) {
//       return true;
//    } else {
//       return confirm('보호자 동의를 받으셨나요?');
//    }
// }

// if (checkAge(age) == true) {
//    alert('접속 허용');
// } else {
//    alert('접속 불가');
// }







// let age = prompt('나이 입력','');

// function checkAge(age) {
//   return (age >= 18) ? true : confirm('보호자 동의를 받으셨나요?');
//  }

//  alert(checkAge(age));
 







// let a = prompt('a',''), b = prompt('b','');

// function min(a,b) {
//    if (a>b){
//       return b;
//    }else return a;
// }

// alert(`min(${a}, ${b}) == ${min(a,b)}`);  