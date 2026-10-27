
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>스마트 키친</title>

  <style>
    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      padding: 30px;
      font-family: "Malgun Gothic", sans-serif;
      background-color: #f5f5f5;
      color: #222;
    }

    .container {
      max-width: 1000px;
      min-height: 650px;
      margin: 0 auto;
      background: white;
      border: 1px solid #999;
    }

    .header {
      margin: 25px auto 20px;
      width: 70%;
      padding: 15px;
      text-align: center;
      font-size: 23px;
      letter-spacing: 5px;
      background: #cfe2f3;
      border: 6px ridge #777;
    }

    .menu-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 35px 45px;
      max-width: 700px;
      margin: 20px auto 40px;
      padding: 0 15px;
    }

    .menu {
      min-height: 180px;
      border-radius: 28% / 35%;
      display: flex;
      justify-content: center;
      align-items: center;
      text-align: center;
      padding: 20px;
      font-size: 19px;
      line-height: 1.7;
      cursor: pointer;
      transition: transform 0.2s, box-shadow 0.2s;
    }

    .menu:hover {
      transform: translateY(-5px);
      box-shadow: 0 6px 14px #0002;
    }

    .menu:focus-visible {
      outline: 3px solid #333;
      outline-offset: 4px;
    }

    .pink {
      background: #f4cccc;
      border: 1px solid #ff6666;
    }

    .orange {
      background: #fce5cd;
      border: 1px solid #ffab66;
    }

    .blue {
      background: #c9daf8;
      border: 1px solid #4d85ff;
    }

    .green {
      background: #d9ead3;
      border: 1px solid #6aa84f;
    }

    .content {
      margin: 0 25px 25px;
      padding: 20px;
      border-top: 1px solid #eee;
      min-height: 80px;
      text-align: center;
      line-height: 1.8;
    }

    @media (max-width: 600px) {
      body {
        padding: 10px;
      }

      .container {
        min-height: 90vh;
      }

      .header {
        width: 90%;
        font-size: 18px;
        letter-spacing: 2px;
      }

      .menu-grid {
        gap: 18px;
      }

      .menu {
        min-height: 140px;
        padding: 10px;
        font-size: 15px;
        border-radius: 25%;
      }
    }
  </style>
</head>

<body>
  <main class="container">

    <header class="header">
      스마트 키친
    </header>

    <section class="menu-grid" aria-label="주요 메뉴">

      <button class="menu pink"
        onclick="showPage('AI 주방 매니저')">
        AI 주방 매니저
      </button>

      <button class="menu orange"
        onclick="showPage('전화 실시간 정리표')">
        전화 실시간 정리표
      </button>

      <button class="menu blue"
        onclick="showPage('주문 폭주 자동 방어 시스템')">
        주문 폭주 자동 방어 시스템
      </button>

      <button class="menu green"
        onclick="showPage('문자 예약 정리 사이트')">
        문자 예약 정리 사이트
      </button>

    </section>

    <section class="content" id="content" aria-live="polite">
      원하는 메뉴를 선택해 주세요.
    </section>

  </main>

  <script>
    function showPage(pageName) {
      const content = document.getElementById("content");

      const descriptions = {
        "AI 주방 매니저":
          "식재료 재고, 조리 순서 및 주방 업무를 관리하는 기능입니다.",

        "전화 실시간 정리표":
          "전화로 접수된 주문과 문의 내용을 실시간으로 정리하는 기능입니다.",

        "주문 폭주 자동 방어 시스템":
          "주문량을 확인하고 주문이 몰릴 때 주방 업무를 효율적으로 관리하는 기능입니다.",

        "문자 예약 정리 사이트":
          "문자로 접수된 예약 내용과 예약 일정을 한눈에 확인하는 기능입니다."
      };

      content.innerHTML =
        "<h2>" + pageName + "</h2>" +
        "<p>" + descriptions[pageName] + "</p>" +
        "<p>선택한 메뉴: " + pageName + "</p>";
    }
  </script>
</body>
</html>
