<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>스마트 키친 | Smart Kitchen Widget Dashboard</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Lucide Icons -->
    <script src="https://unpkg.com/lucide@latest"></script>
    <!-- Google Font: Plus Jakarta Sans & Noto Sans KR -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">

    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Plus Jakarta Sans', 'Noto Sans KR', 'sans-serif'],
                    },
                    colors: {
                        slateTheme: {
                            50: '#f4f6f9',
                            100: '#e8ecf2',
                            200: '#d1d9e5',
                            300: '#a3b4cc',
                            400: '#728cae',
                            500: '#4e698d',
                            600: '#3a506e',
                            700: '#2d3e56',
                            800: '#1e293b',
                            900: '#0f172a',
                        },
                        accentTeal: '#4a7c82',
                        accentDark: '#202832',
                    },
                    borderRadius: {
                        '4xl': '2rem',
                        '5xl': '2.5rem',
                    }
                }
            }
        }
    </script>
    <style>
        body {
            font-family: 'Plus Jakarta Sans', 'Noto Sans KR', sans-serif;
            background: radial-gradient(circle at 10% 20%, rgba(138, 160, 194, 0.45) 0%, rgba(198, 208, 222, 0.3) 40%, rgba(226, 232, 240, 0.8) 90%),
                        radial-gradient(circle at 90% 80%, rgba(74, 124, 130, 0.3) 0%, rgba(160, 178, 200, 0.2) 50%, rgba(241, 245, 249, 1) 100%);
            background-attachment: fixed;
            min-height: 100vh;
        }

        /* Modern Soft Widget Shadow & Card Styling */
        .widget-card {
            background: rgba(255, 255, 255, 0.82);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.8);
            box-shadow: 0 20px 40px -15px rgba(30, 41, 59, 0.07), 0 0 1px 1px rgba(255, 255, 255, 0.9) inset;
            border-radius: 2rem;
            transition: transform 0.25s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.25s ease;
        }

        .widget-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 25px 50px -12px rgba(30, 41, 59, 0.12), 0 0 1px 1px rgba(255, 255, 255, 1) inset;
        }

        .widget-card-dark {
            background: rgba(32, 40, 50, 0.92);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.12);
            box-shadow: 0 20px 40px -15px rgba(15, 23, 42, 0.3);
            border-radius: 2rem;
            color: #f8fafc;
        }

        .widget-card-teal {
            background: linear-gradient(145deg, rgba(82, 118, 126, 0.9), rgba(58, 86, 92, 0.95));
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 20px 40px -15px rgba(38, 65, 70, 0.25);
            border-radius: 2rem;
            color: #ffffff;
        }

        .widget-card-blue {
            background: linear-gradient(145deg, rgba(110, 134, 168, 0.88), rgba(80, 105, 138, 0.92));
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 20px 40px -15px rgba(45, 62, 86, 0.2);
            border-radius: 2rem;
            color: #ffffff;
        }

        /* Pill scrollbar */
        .custom-scroll::-webkit-scrollbar {
            width: 5px;
            height: 5px;
        }
        .custom-scroll::-webkit-scrollbar-track {
            background: transparent;
        }
        .custom-scroll::-webkit-scrollbar-thumb {
            background: rgba(148, 163, 184, 0.3);
            border-radius: 10px;
        }
        .custom-scroll::-webkit-scrollbar-thumb:hover {
            background: rgba(148, 163, 184, 0.6);
        }
    </style>
</head>
<body class="text-slate-800 antialiased p-4 sm:p-6 lg:p-10 min-h-screen flex flex-col justify-between">

    <!-- Header Section -->
    <header class="max-w-7xl mx-auto w-full mb-8">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div class="flex items-center gap-4">
                <div class="w-12 h-12 bg-slateTheme-800 text-white rounded-2xl flex items-center justify-center shadow-lg shadow-slate-900/10">
                    <i data-lucide="utensils" class="w-6 h-6"></i>
                </div>
                <div>
                    <div class="flex items-center gap-2">
                        <h1 class="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900">스마트 키친</h1>
                        <span class="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-700 font-bold border border-emerald-500/20 flex items-center gap-1">
                            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> LIVE
                        </span>
                    </div>
                    <p class="text-xs text-slate-500 font-medium">통합 주방 자동화 대시보드 시스템</p>
                </div>
            </div>

            <!-- Top Controls / Quick Status -->
            <div class="flex items-center gap-3 w-full sm:w-auto overflow-x-auto pb-1 sm:pb-0">
                <div class="bg-white/80 backdrop-blur-md px-4 py-2.5 rounded-2xl border border-white/60 shadow-sm flex items-center gap-3 shrink-0">
                    <i data-lucide="clock" class="w-4 h-4 text-slate-400"></i>
                    <span id="currentTime" class="font-mono text-xs font-bold text-slate-700">14:45:00</span>
                </div>
                <div class="bg-white/80 backdrop-blur-md px-4 py-2.5 rounded-2xl border border-white/60 shadow-sm flex items-center gap-3 shrink-0">
                    <i data-lucide="activity" class="w-4 h-4 text-teal-600"></i>
                    <span class="text-xs font-semibold text-slate-600">주방 상태: <span class="text-teal-700 font-bold">정상 가동 중</span></span>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Widget Grid Layout (Matching Reference Aesthetic) -->
    <main class="max-w-7xl mx-auto w-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8 flex-1">

        <!-- ========================================== -->
        <!-- WIDGET 1: AI 주방매니저 (Large Widget - 2 cols) -->
        <!-- ========================================== -->
        <section class="widget-card p-6 md:col-span-2 flex flex-col justify-between">
            <div>
                <!-- Card Header -->
                <div class="flex items-center justify-between mb-5">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-2xl bg-slateTheme-100 text-slateTheme-700 flex items-center justify-center">
                            <i data-lucide="bot" class="w-5 h-5"></i>
                        </div>
                        <div>
                            <h2 class="font-bold text-slate-900 text-lg leading-tight">AI 주방매니저</h2>
                            <p class="text-xs text-slate-400 font-medium">조리 순서 최적화 & AI 가이드</p>
                        </div>
                    </div>
                    <button onclick="addOrderSim()" class="text-xs font-bold bg-slateTheme-800 hover:bg-slateTheme-900 text-white px-3.5 py-2 rounded-xl transition shadow-sm flex items-center gap-1.5">
                        <i data-lucide="plus" class="w-3.5 h-3.5"></i> 신규 주문
                    </button>
                </div>

                <!-- AI Advice Banner -->
                <div class="bg-slateTheme-50 border border-slateTheme-200/80 rounded-2xl p-3.5 mb-4 flex items-start gap-3">
                    <div class="p-1.5 bg-amber-500/10 text-amber-600 rounded-lg shrink-0 mt-0.5">
                        <i data-lucide="sparkles" class="w-4 h-4"></i>
                    </div>
                    <div>
                        <span class="text-xs font-bold text-slate-800">AI 스마트 추천:</span>
                        <p id="aiAdviceText" class="text-xs text-slate-600 mt-0.5">파스타와 스테이크 조리 완료 타이밍을 맞추기 위해 3번 테이블 스테이크 시어링을 먼저 시작하세요.</p>
                    </div>
                </div>

                <!-- Live Orders List -->
                <div class="space-y-2.5 max-h-[220px] overflow-y-auto custom-scroll pr-1" id="orderQueueContainer">
                    <!-- Dynamic Orders Inserted Here -->
                </div>
            </div>

            <!-- Footer Summary -->
            <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-medium text-slate-500">
                <span>대기 중인 조리: <strong id="pendingCount" class="text-slate-800 font-bold">3건</strong></span>
                <span class="flex items-center gap-1 text-slate-400">
                    <i data-lucide="check-circle-2" class="w-3.5 h-3.5 text-emerald-500"></i> AI 라우팅 활성화
                </span>
            </div>
        </section>


        <!-- ========================================== -->
        <!-- WIDGET 2: 전화 실시간 정리표 (Dark Theme Widget) -->
        <!-- ========================================== -->
        <section class="widget-card-dark p-6 flex flex-col justify-between">
            <div>
                <!-- Header -->
                <div class="flex items-center justify-between mb-4">
                    <div class="flex items-center gap-2.5">
                        <div class="w-9 h-9 rounded-xl bg-white/10 text-teal-300 flex items-center justify-center">
                            <i data-lucide="phone-call" class="w-4 h-4"></i>
                        </div>
                        <h2 class="font-bold text-white text-base">전화 실시간 정리표</h2>
                    </div>
                    <span class="text-[10px] bg-teal-500/20 text-teal-300 border border-teal-500/30 font-bold px-2 py-0.5 rounded-full">STT AI</span>
                </div>

                <p class="text-xs text-slate-400 mb-3">전화 문의 내용을 실시간 텍스트 요약합니다.</p>

                <!-- Call List Container -->
                <div class="space-y-2.5 max-h-[220px] overflow-y-auto custom-scroll pr-1" id="callListContainer">
                    <!-- Dynamic Calls Inserted Here -->
                </div>
            </div>

            <div class="mt-4 pt-3 border-t border-white/10 flex items-center justify-between">
                <button onclick="triggerIncomingCall()" class="w-full bg-white/10 hover:bg-white/20 text-white text-xs font-semibold py-2 rounded-xl transition border border-white/10 flex items-center justify-center gap-2">
                    <i data-lucide="phone-incoming" class="w-3.5 h-3.5 text-teal-400 animate-bounce"></i>
                    가상 전화 수신 테스트
                </button>
            </div>
        </section>


        <!-- ========================================== -->
        <!-- WIDGET 3: 주문 폭주 자동 방어 시스템 (Teal Widget) -->
        <!-- ========================================== -->
        <section class="widget-card-teal p-6 flex flex-col justify-between">
            <div>
                <!-- Header -->
                <div class="flex items-center justify-between mb-4">
                    <div class="flex items-center gap-2.5">
                        <div class="w-9 h-9 rounded-xl bg-white/15 text-white flex items-center justify-center">
                            <i data-lucide="shield-alert" class="w-4 h-4"></i>
                        </div>
                        <h2 class="font-bold text-white text-base">주문 폭주 방어</h2>
                    </div>
                    <!-- Toggle Switch -->
                    <label class="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" id="defenseToggle" class="sr-only peer" checked onchange="toggleDefenseMode()">
                        <div class="w-11 h-6 bg-white/30 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-white/90"></div>
                    </label>
                </div>

                <p class="text-xs text-emerald-100/80 mb-4">주방 과부하 시 배달 및 접수를 자동 조절합니다.</p>

                <!-- Kitchen Meter Status -->
                <div class="bg-black/20 p-4 rounded-2xl border border-white/10 space-y-3">
                    <div class="flex justify-between items-center text-xs">
                        <span class="text-emerald-100 font-medium">주방 과부하율</span>
                        <span id="loadText" class="font-extrabold text-amber-300">78% (혼잡)</span>
                    </div>

                    <div class="w-full bg-white/20 rounded-full h-3 overflow-hidden">
                        <div id="loadBar" class="bg-amber-300 h-full rounded-full transition-all duration-500" style="width: 78%"></div>
                    </div>

                    <div class="flex justify-between text-[11px] text-emerald-100/70 pt-1">
                        <span>예상 대기: +15분</span>
                        <span>간격 접수: ON</span>
                    </div>
                </div>
            </div>

            <!-- Simulation Controls -->
            <div class="mt-4 pt-3 border-t border-white/10 flex items-center justify-between gap-1">
                <button onclick="setKitchenLoad(45)" class="flex-1 py-1.5 text-[11px] font-semibold bg-white/10 hover:bg-white/20 rounded-lg text-white transition">45%</button>
                <button onclick="setKitchenLoad(78)" class="flex-1 py-1.5 text-[11px] font-semibold bg-white/10 hover:bg-white/20 rounded-lg text-white transition">78%</button>
                <button onclick="setKitchenLoad(92)" class="flex-1 py-1.5 text-[11px] font-bold bg-amber-400/30 hover:bg-amber-400/40 text-amber-200 rounded-lg transition">92% (폭주)</button>
            </div>
        </section>


        <!-- ========================================== -->
        <!-- WIDGET 4: 문자 예약 정리 사이트 (Slate Blue Card) -->
        <!-- ========================================== -->
        <section class="widget-card p-6 lg:col-span-3 flex flex-col justify-between">
            <div>
                <!-- Header -->
                <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-4">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-2xl bg-slateTheme-100 text-slateTheme-700 flex items-center justify-center">
                            <i data-lucide="message-square" class="w-5 h-5"></i>
                        </div>
                        <div>
                            <h2 class="font-bold text-slate-900 text-lg leading-tight">문자 예약 정리 사이트</h2>
                            <p class="text-xs text-slate-400 font-medium">수신 문자 자동 파싱 및 예약 대장 통합 관리</p>
                        </div>
                    </div>
                    <button onclick="simIncomingSMS()" class="text-xs font-semibold bg-slateTheme-100 hover:bg-slateTheme-200 text-slateTheme-800 px-3.5 py-2 rounded-xl transition flex items-center gap-1.5">
                        <i data-lucide="send" class="w-3.5 h-3.5 text-slateTheme-600"></i> 가상 SMS 수신
                    </button>
                </div>

                <!-- Table Container -->
                <div class="overflow-x-auto rounded-2xl border border-slate-100 bg-white/60">
                    <table class="w-full text-left text-xs">
                        <thead>
                            <tr class="bg-slate-100/70 border-b border-slate-100 text-slate-500 font-semibold">
                                <th class="p-3">예약자</th>
                                <th class="p-3">일시</th>
                                <th class="p-3">인원</th>
                                <th class="p-3">파싱 원문 내용</th>
                                <th class="p-3 text-center">상태</th>
                                <th class="p-3 text-right">관리</th>
                            </tr>
                        </thead>
                        <tbody id="smsTableBody">
                            <!-- Dynamic Rows -->
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
                <span>오늘 총 예약: <strong class="text-slate-700 font-bold" id="totalResCount">3건</strong></span>
                <span class="text-[11px]">SMS 파싱 엔진 2.0 작동 중</span>
            </div>
        </section>


        <!-- ========================================== -->
        <!-- WIDGET 5: Quick Stats Tile Widget -->
        <!-- ========================================== -->
        <section class="widget-card-blue p-6 flex flex-col justify-between">
            <div>
                <div class="flex items-center justify-between mb-3">
                    <span class="text-xs font-medium text-slate-200">오늘의 요약</span>
                    <i data-lucide="bar-chart-2" class="w-4 h-4 text-slate-200"></i>
                </div>

                <div class="space-y-4">
                    <div>
                        <div class="text-[11px] text-slate-200">총 처리 주문</div>
                        <div class="text-2xl font-extrabold text-white">48<span class="text-xs font-normal text-slate-200 ml-1">건</span></div>
                    </div>
                    <div>
                        <div class="text-[11px] text-slate-200">평균 조리 완료 시간</div>
                        <div class="text-2xl font-extrabold text-white">12<span class="text-xs font-normal text-slate-200 ml-1">분</span></div>
                    </div>
                </div>
            </div>

            <div class="pt-3 border-t border-white/20">
                <div class="flex items-center justify-between text-[11px] text-slate-100">
                    <span>주방 효율성</span>
                    <span class="font-bold text-white">+18% 상승</span>
                </div>
            </div>
        </section>

    </main>

    <!-- Footer -->
    <footer class="max-w-7xl mx-auto w-full text-center text-xs text-slate-500 py-2">
        Smart Kitchen Modern Widget Dashboard &copy; 2026. All rights reserved.
    </footer>


    <!-- JAVASCRIPT LOGIC -->
    <script>
        // ----------------------------------------------------
        // State Data
        // ----------------------------------------------------
        let orders = [
            { id: 101, table: "3번 테이블", name: "안심 스테이크 (Medium)", time: "8분 전", status: "조리중", priority: "high" },
            { id: 102, table: "5번 테이블", name: "해산물 봉골레 파스타", time: "4분 전", status: "조리중", priority: "normal" },
            { id: 103, table: "1번 테이블", name: "마르게리타 피자", time: "1분 전", status: "대기", priority: "normal" }
        ];

        let calls = [
            { id: 1, phone: "010-3812-****", tag: "예약", summary: "오늘 18:30 4명 창가석 예약", time: "14:20" },
            { id: 2, phone: "010-9102-****", tag: "포장", summary: "파스타 세트 방문포장 20분뒤", time: "13:55" },
            { id: 3, phone: "010-4491-****", tag: "문의", summary: "주차 가능 여부 문의", time: "12:10" }
        ];

        let smsList = [
            { id: 1, name: "김지훈", date: "10/28 18:30", count: "3명", raw: "내일 6시반 3명 예약 가능한가요?", status: "확정" },
            { id: 2, name: "박서연", date: "10/28 19:00", count: "6명", raw: "10/28 19:00 6명 단체석 문의드립니다", status: "대기" },
            { id: 3, name: "이현우", date: "10/29 12:00", count: "2명", raw: "모레 점심 12시 2명 예약이요", status: "확정" }
        ];

        // ----------------------------------------------------
        // Init & Clock
        // ----------------------------------------------------
        window.onload = function() {
            lucide.createIcons();
            updateClock();
            setInterval(updateClock, 1000);
            renderOrders();
            renderCalls();
            renderSMS();
        };

        function updateClock() {
            const now = new Date();
            document.getElementById('currentTime').innerText = now.toTimeString().split(' ')[0];
        }

        // ----------------------------------------------------
        // 1. AI 주방매니저 Render & Handlers
        // ----------------------------------------------------
        function renderOrders() {
            const container = document.getElementById('orderQueueContainer');
            container.innerHTML = '';

            document.getElementById('pendingCount').innerText = `${orders.length}건`;

            orders.forEach(order => {
                let badgeClass = order.status === '조리중' ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-600';
                let priorityBorder = order.priority === 'high' ? 'border-l-4 border-amber-500' : 'border-slate-100';

                const div = document.createElement('div');
                div.className = `bg-white p-3 rounded-2xl border ${priorityBorder} shadow-sm flex items-center justify-between text-xs gap-2`;
                div.innerHTML = `
                    <div class="space-y-0.5">
                        <div class="flex items-center gap-1.5">
                            <span class="font-bold text-slate-800">${order.table}</span>
                            <span class="text-[10px] px-2 py-0.5 rounded-full font-bold ${badgeClass}">${order.status}</span>
                            <span class="text-[10px] text-slate-400">(${order.time})</span>
                        </div>
                        <div class="text-slate-600 font-medium">${order.name}</div>
                    </div>
                    <div class="flex items-center gap-1">
                        <button onclick="finishOrder(${order.id})" class="px-2.5 py-1.5 bg-slateTheme-800 hover:bg-slateTheme-900 text-white font-semibold rounded-xl transition text-[11px]">
                            완료
                        </button>
                    </div>
                `;
                container.appendChild(div);
            });
        }

        function finishOrder(id) {
            orders = orders.filter(o => o.id !== id);
            renderOrders();
        }

        function addOrderSim() {
            const items = ["크림 리조또", "채끝 등심 스테이크", "고르곤졸라 피자", "쉬림프 알리오 올리오"];
            const randItem = items[Math.floor(Math.random() * items.length)];
            const randTable = `${Math.floor(Math.random() * 8) + 1}번 테이블`;

            orders.unshift({
                id: Date.now(),
                table: randTable,
                name: randItem,
                time: "방금 전",
                status: "대기",
                priority: "normal"
            });
            renderOrders();
        }

        // ----------------------------------------------------
        // 2. 전화 실시간 정리표 Render & Handlers
        // ----------------------------------------------------
        function renderCalls() {
            const container = document.getElementById('callListContainer');
            container.innerHTML = '';

            calls.forEach(call => {
                let tagBg = 'bg-white/10 text-slate-200';
                if(call.tag === '예약') tagBg = 'bg-teal-500/20 text-teal-300 border border-teal-500/30';
                if(call.tag === '포장') tagBg = 'bg-blue-500/20 text-blue-300 border border-blue-500/30';

                const div = document.createElement('div');
                div.className = 'bg-white/5 p-3 rounded-2xl border border-white/10 text-xs space-y-1';
                div.innerHTML = `
                    <div class="flex items-center justify-between text-[11px]">
                        <span class="font-bold text-slate-200">${call.phone}</span>
                        <span class="text-slate-400">${call.time}</span>
                    </div>
                    <div class="text-slate-300 text-[11px] flex items-center gap-1.5">
                        <span class="text-[9px] px-1.5 py-0.5 rounded ${tagBg}">${call.tag}</span>
                        <span class="truncate">${call.summary}</span>
                    </div>
                `;
                container.appendChild(div);
            });
        }

        function triggerIncomingCall() {
            const samples = [
                { tag: "예약", summary: "내일 저녁 7시 6명 단체석 예약 문의" },
                { tag: "포장", summary: "스테이크 샐러드 1개 포장 예약" },
                { tag: "문의", summary: "콜키지 가능 여부 및 금액 문의" }
            ];
            const rand = samples[Math.floor(Math.random() * samples.length)];
            const now = new Date();
            const timeStr = `${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}`;

            calls.unshift({
                id: Date.now(),
                phone: `010-${Math.floor(1000+Math.random()*9000)}-****`,
                tag: rand.tag,
                summary: rand.summary,
                time: timeStr
            });
            renderCalls();
        }

        // ----------------------------------------------------
        // 3. 주문 폭주 자동 방어 Handler
        // ----------------------------------------------------
        function toggleDefenseMode() {
            const checked = document.getElementById('defenseToggle').checked;
            if(!checked) {
                document.getElementById('loadText').innerText = "방어 비활성화";
                document.getElementById('loadText').className = "font-extrabold text-slate-300";
            } else {
                setKitchenLoad(78);
            }
        }

        function setKitchenLoad(percent) {
            const bar = document.getElementById('loadBar');
            const text = document.getElementById('loadText');
            bar.style.width = `${percent}%`;

            if(percent >= 90) {
                text.innerText = `${percent}% (폭주/제어)`;
                text.className = "font-extrabold text-red-300";
                bar.className = "bg-red-400 h-full rounded-full transition-all duration-500";
            } else if(percent >= 70) {
                text.innerText = `${percent}% (혼잡)`;
                text.className = "font-extrabold text-amber-300";
                bar.className = "bg-amber-300 h-full rounded-full transition-all duration-500";
            } else {
                text.innerText = `${percent}% (여유)`;
                text.className = "font-extrabold text-emerald-200";
                bar.className = "bg-emerald-300 h-full rounded-full transition-all duration-500";
            }
        }

        // ----------------------------------------------------
        // 4. 문자 예약 정리 사이트 Render & Handlers
        // ----------------------------------------------------
        function renderSMS() {
            const tbody = document.getElementById('smsTableBody');
            tbody.innerHTML = '';
            document.getElementById('totalResCount').innerText = `${smsList.length}건`;

            smsList.forEach(item => {
                let badge = item.status === '확정' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800';

                const tr = document.createElement('tr');
                tr.className = "border-b border-slate-100 hover:bg-slate-50/50 transition";
                tr.innerHTML = `
                    <td class="p-3 font-bold text-slate-800">${item.name}</td>
                    <td class="p-3 text-slate-600">${item.date}</td>
                    <td class="p-3 text-slate-700">${item.count}</td>
                    <td class="p-3 text-slate-400 text-[11px] truncate max-w-[200px]">${item.raw}</td>
                    <td class="p-3 text-center">
                        <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${badge}">${item.status}</span>
                    </td>
                    <td class="p-3 text-right">
                        <button onclick="toggleSMSStatus(${item.id})" class="text-[10px] font-bold text-slate-600 bg-slate-100 hover:bg-slate-200 px-2 py-1 rounded-lg">
                            ${item.status === '확정' ? '대기로' : '승인'}
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        function toggleSMSStatus(id) {
            smsList = smsList.map(item => {
                if(item.id === id) {
                    return { ...item, status: item.status === '확정' ? '대기' : '확정' };
                }
                return item;
            });
            renderSMS();
        }

        function simIncomingSMS() {
            const names = ["정민우", "최수아", "강태양"];
            const name = names[Math.floor(Math.random() * names.length)];
            const count = `${Math.floor(Math.random() * 4) + 2}명`;

            smsList.unshift({
                id: Date.now(),
                name: name,
                date: "10/30 19:30",
                count: count,
                raw: `10/30 19:30 ${count} 예약 신청합니다. (${name})`,
                status: "대기"
            });
            renderSMS();
        }
    </script>
</body>
</html>
