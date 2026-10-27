<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>스마트 키친 (Smart Kitchen) 대시보드</title>
  <style>
    :root {
      --bg-gradient: linear-gradient(135deg, #abb9d3 0%, #8ca1c2 40%, #b8c8d8 70%, #9cb2c9 100%);
      --card-bg-light: rgba(255, 255, 255, 0.85);
      --card-bg-dark: #273142;
      --card-bg-teal: #3d6a7d;
      --card-bg-slate: #5b6e8a;
      --text-dark: #1e293b;
      --text-light: #f8fafc;
      --text-muted: #64748b;
      --accent-blue: #3b82f6;
      --accent-green: #10b981;
      --accent-orange: #f59e0b;
      --accent-red: #ef4444;
      --radius-xl: 28px;
      --radius-lg: 20px;
      --radius-md: 14px;
      --shadow-soft: 0 10px 30px rgba(0, 0, 0, 0.08);
      --font-main: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: var(--font-main);
    }

    body {
      background: var(--bg-gradient);
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 24px;
      color: var(--text-dark);
    }

    .app-container {
      width: 100%;
      max-width: 1200px;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    /* Header Styling */
    .app-header {
      background: rgba(255, 255, 255, 0.65);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid rgba(255, 255, 255, 0.5);
      border-radius: var(--radius-xl);
      padding: 20px 28px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: var(--shadow-soft);
    }

    .header-title-zone h1 {
      font-size: 24px;
      font-weight: 700;
      color: #1e293b;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .header-title-zone p {
      font-size: 13px;
      color: var(--text-muted);
      margin-top: 4px;
    }

    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(16, 185, 129, 0.15);
      color: #065f46;
      padding: 8px 16px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: 600;
    }

    .status-dot {
      width: 8px;
      height: 8px;
      background-color: #10b981;
      border-radius: 50%;
      animation: pulse 2s infinite;
    }

    @keyframes pulse {
      0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
      70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
      100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    /* Main Grid Layout */
    .dashboard-grid {
      display: grid;
      grid-template-columns: repeat(12, 1fr);
      gap: 20px;
    }

    /* Base Card Style */
    .widget-card {
      border-radius: var(--radius-xl);
      padding: 24px;
      box-shadow: var(--shadow-soft);
      transition: transform 0.2s ease, box-shadow 0.2s ease;
      display: flex;
      flex-direction: column;
      position: relative;
      overflow: hidden;
    }

    .widget-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 14px 35px rgba(0,0,0,0.12);
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
    }

    .card-title {
      font-size: 18px;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .card-btn {
      background: rgba(255, 255, 255, 0.2);
      border: none;
      color: inherit;
      padding: 8px 14px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      backdrop-filter: blur(4px);
      transition: background 0.2s;
    }

    .card-btn:hover {
      background: rgba(255, 255, 255, 0.35);
    }

    /* Card Themes */
    .card-white {
      background: var(--card-bg-light);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.6);
      color: var(--text-dark);
    }

    .card-dark {
      background: var(--card-bg-dark);
      color: var(--text-light);
    }

    .card-teal {
      background: var(--card-bg-teal);
      color: var(--text-light);
    }

    .card-slate {
      background: var(--card-bg-slate);
      color: var(--text-light);
    }

    /* Specific Grid Spans */
    .span-7 { grid-column: span 7; }
    .span-5 { grid-column: span 5; }
    .span-6 { grid-column: span 6; }

    @media (max-width: 900px) {
      .span-7, .span-5, .span-6 { grid-column: span 12; }
    }

    /* Common List & Elements */
    .item-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
      flex: 1;
    }

    .list-item {
      padding: 14px;
      border-radius: var(--radius-md);
      display: flex;
      justify-content: space-between;
      align-items: center;
      transition: background 0.2s;
    }

    .card-white .list-item {
      background: rgba(241, 245, 249, 0.8);
    }

    .card-dark .list-item,
    .card-teal .list-item,
    .card-slate .list-item {
      background: rgba(255, 255, 255, 0.1);
    }

    .tag {
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
    }

    .tag-blue { background: rgba(59, 130, 246, 0.2); color: #2563eb; }
    .tag-green { background: rgba
