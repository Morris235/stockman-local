/*
<Jest 설명>
yarn test 명령을 사용하면 프로젝트 내에 모든 테스트 파일을 찾아서 테스트를 실행해준다.
jest는 기본적으로 test.js로 끝나거나 _test_ 디렉터리 안에 있는 파일들을 모두 테스트 파일로 인식한다. 
만약 특정 테스트 파일만 실행하고 싶은 경우에는 yarn test <파일명 이나 경로>를 입력하면된다.

<자주 사용되는 Matcher>
jest에서는 거의 상상 가능한 모든 경우에 대한 Matcher 함수를 제공하고 있다.
toBe() : 문자열이 정확히 일치하는지 체크
toEqual() : 객체 검증할 때 사용?
toBeTruthy() : 검증 대상이 이 규칙에 따라 true로 간주되면 테스트 통과
toBeFalsy() : 검증 대상이 이 규칙에 따라 false로 간주되는 경우 테스트 통과
toHaveLenght() : 배열의 길이를 체크
toContain() : 특정 원소가 배열에 들어있는지를 테스트
toMatch() : 정규식 기반의 문자열 테스트 
toThrow() : 예외 발생 여부 테스트 
(expact() 함수에 넘기는 검증 대상을 함수로 한 번 감싸줘야 함, 테스트 실행 도중 정말 해당 예외가 발생하기 때문에 테스트는 항상 실패한다.)

<기본 사용 패턴>
 test("테스트 설명", ()=> {
    expect("검증 대상").toXxx("기대결과");
 });

 // toXxx는 Test Matcher다. 
*/  

// 테스트 해볼 함수
const getUser = (id) => {
   return {
      id,
      email: `user${id}@test.com`,
   };
};

const getUserThrow = (id) => {
   if(id <= 0) throw new Error("Invalid ID");
   return {
      id,
      email: `user${id}@test.com`,
   };
};


// 테스트 실행
test("1 is 1", () => {
   expect(1).toBe(1);
 });

test("return a user object", () => {
   expect(getUser(1)).toEqual({
      id: 1,
      email: `user1@test.com`,
   });
});

test("number 0 is falsy but string 0 is truthy", () => {
   expect(0).toBeFalsy();
   expect("0").toBeTruthy();
});

test("array test", () => {
   const colors = ["Red", "Yellow", "Blue"];

   expect(colors).toHaveLength(3);
   expect(colors).toContain("Yellow");
   expect(colors).not.toContain("Green");
});

test("string", () => {
   expect(getUser(1).email).toBe("user1@test.com");
   expect(getUser(2).email).toMatch(/.*test.com$/);
});

test("throw when id is non negative", () => {
   expect(() => getUserThrow(-1)).toThrow();
   // expect(() => getUserThrow(-1)).toThrow("Invalid ID");
});