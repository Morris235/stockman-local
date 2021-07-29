// LinkedList 구현
export default function LinkedList () {
    this.head = new node("head");
    this.find = find;
    this.append = append;
    this.insert = insert;
    this.remove = remove;
    this.findPre = findPre;
    this.element = element;

// node 구현
function node(data, next=null){
    this.data = data;
    this.next = next;
};

// 노드 찾기
function find (item) {
    let currNode = this.head;
    while (currNode.data !== item) {
        currNode = currNode.next;
    }
    return currNode;
};

// 이전 노드 찾기
function findPre (item) {
    let currNode = this.head;
    while (currNode.next != null && currNode.next.data != item) {
        currNode = currNode.next;
    }
    return currNode;
};

// 노드 추가
function append (newData) {
    let newNode = new node(newData);  // 새로운 노드 생성
    let current = this.head;  // 시작 노드
    while (current.next != null) {  // 맨 끝 노드 찾기
        current = current.next;
    }
    current.next = newNode;
};

// 노드 중간 삽입
function insert (newData, item) {
    let newNode = new node(newData);  // 새로운 노드 생성
    let current = this.find(item);  // 삽입할 위치의 노드 찾기
    newNode.next = current.next;  // 찾은 노드가 가리키는 노드를 새로운 노드가 가리키기
    current.next = newNode;  // 찾은 노드는 이제부터 새로운 노드를 가리키도록 하기
};

// 노드 삭제
function remove (item) {
    let preNode = this.findPre(item);  // 삭제할 노드를 가리키는 노드 찾기
    preNode.next = preNode.next.next;  // 삭제할 노드 다음 노드를 가리키도록 하기
};

// 연결 리스트의 요소들을 출력 
function element () {
    let data = [];
    let currNode = this.head;
    while (currNode.next != null) {
        data.push(currNode.next.data);
        currNode = currNode.next;
    };
    return data;
};
};

