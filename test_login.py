from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # 1. 测试登录页面
    print("1. 测试登录页面...")
    page.goto('http://localhost:3000/login')
    page.wait_for_load_state('networkidle')
    page.screenshot(path='/tmp/login.png', full_page=True)
    print("   登录页面截图已保存: /tmp/login.png")

    # 2. 填写登录信息
    print("2. 填写登录信息...")
    page.fill('input[placeholder="请输入用户名"]', 'admin')
    page.fill('input[placeholder="请输入密码"]', 'admin123')
    page.screenshot(path='/tmp/login_filled.png', full_page=True)

    # 3. 点击登录按钮
    print("3. 点击登录按钮...")
    page.click('button:has-text("登 录")')
    page.wait_for_timeout(3000)

    # 4. 检查是否跳转
    print(f"4. 当前URL: {page.url}")
    page.screenshot(path='/tmp/after_login.png', full_page=True)

    if '/login' not in page.url:
        print("   ✅ 登录成功，已跳转到首页！")

        # 5. 检查侧边栏菜单
        print("5. 检查侧边栏设备管理菜单...")
        page.wait_for_timeout(1000)
        page.screenshot(path='/tmp/sidebar.png', full_page=True)

        # 6. 测试违停球页面
        print("6. 测试违停球页面...")
        page.click('text=违停球')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(1000)
        page.screenshot(path='/tmp/parking.png', full_page=True)
        print(f"   当前URL: {page.url}")

        # 7. 测试卡口页面
        print("7. 测试卡口页面...")
        page.click('text=卡口')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(1000)
        page.screenshot(path='/tmp/checkpoint.png', full_page=True)
        print(f"   当前URL: {page.url}")

        # 8. 测试后端设备页面
        print("8. 测试后端设备页面...")
        page.click('text=后端设备')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(1000)
        page.screenshot(path='/tmp/backend.png', full_page=True)
        print(f"   当前URL: {page.url}")

    else:
        print("   ❌ 登录失败，仍在登录页面")

    browser.close()
    print("\n测试完成！")
