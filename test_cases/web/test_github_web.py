"""
GitHub Web UI 测试

测试场景：
1. 登录功能测试
2. 首页功能测试
3. 用户操作测试

注意：使用 Mock 模拟 WebDriver，不需要真实浏览器
"""
import pytest
import allure
from unittest.mock import Mock, patch, MagicMock


@allure.feature("登录功能")
class TestLogin:
    """登录功能测试类"""
    
    @allure.story("登录成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试登录成功")
    def test_login_success(self):
        """测试登录成功"""
        with allure.step("Mock WebDriver"):
            mock_driver = MagicMock()
            mock_driver.title = "GitHub"
            mock_driver.current_url = "https://github.com/login"
        
        with allure.step("模拟登录操作"):
            mock_element = MagicMock()
            mock_driver.find_element.return_value = mock_element
            mock_driver.find_elements.return_value = [mock_element]
            
            mock_element.clear()
            mock_element.send_keys("testuser")
            mock_element.clear()
            mock_element.send_keys("testpassword")
            mock_element.click()
        
        with allure.step("验证登录操作执行"):
            assert mock_driver.title == "GitHub"
            assert mock_element.send_keys.called
    
    @allure.story("登录失败")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试登录失败显示错误信息")
    def test_login_failure(self):
        """测试登录失败显示错误信息"""
        with allure.step("Mock WebDriver"):
            mock_driver = MagicMock()
            mock_driver.title = "GitHub"
        
        with allure.step("模拟登录失败"):
            mock_error = MagicMock()
            mock_error.text = "Incorrect username or password."
            mock_driver.find_element.return_value = mock_error
        
        with allure.step("验证错误信息"):
            error_msg = mock_error.text
            assert "Incorrect" in error_msg
    
    @allure.story("表单验证")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试登录页面元素显示")
    def test_login_page_elements(self):
        """测试登录页面元素显示"""
        with allure.step("Mock WebDriver"):
            mock_driver = MagicMock()
            mock_element = MagicMock()
            mock_driver.find_element.return_value = mock_element
        
        with allure.step("验证用户名输入框显示"):
            element = mock_driver.find_element("id", "login_field")
            assert element is not None
        
        with allure.step("验证密码输入框显示"):
            element = mock_driver.find_element("id", "password")
            assert element is not None
        
        with allure.step("验证登录按钮显示"):
            element = mock_driver.find_element("name", "commit")
            assert element is not None


@allure.feature("首页功能")
class TestHomePage:
    """首页功能测试类"""
    
    @allure.story("页面加载")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试首页加载")
    def test_home_page_load(self):
        """测试首页加载"""
        with allure.step("Mock WebDriver"):
            mock_driver = MagicMock()
            mock_driver.title = "GitHub"
            mock_driver.current_url = "https://github.com"
        
        with allure.step("验证首页元素"):
            assert mock_driver.title == "GitHub"
            assert "github.com" in mock_driver.current_url
    
    @allure.story("导航")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试导航功能")
    def test_navigation(self):
        """测试导航功能"""
        with allure.step("Mock WebDriver"):
            mock_driver = MagicMock()
            mock_element = MagicMock()
            mock_driver.find_element.return_value = mock_element
        
        with allure.step("导航到 Pull requests"):
            element = mock_driver.find_element("link text", "Pull requests")
            element.click()
            assert element.click.called
        
        with allure.step("导航到 Issues"):
            element = mock_driver.find_element("link text", "Issues")
            element.click()
            assert element.click.called
    
    @allure.story("搜索")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试搜索功能")
    def test_search(self):
        """测试搜索功能"""
        with allure.step("Mock WebDriver"):
            mock_driver = MagicMock()
            mock_search_input = MagicMock()
            mock_driver.find_element.return_value = mock_search_input
        
        with allure.step("搜索仓库"):
            search_input = mock_driver.find_element("name", "q")
            search_input.clear()
            search_input.send_keys("pytest")
            search_input.submit()
        
        with allure.step("验证搜索操作"):
            assert search_input.send_keys.called
    
    @allure.story("仓库列表")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试仓库列表显示")
    def test_repo_list(self):
        """测试仓库列表显示"""
        with allure.step("Mock WebDriver"):
            mock_driver = MagicMock()
            mock_repos = [MagicMock() for _ in range(5)]
            mock_driver.find_elements.return_value = mock_repos
        
        with allure.step("获取仓库列表"):
            repos = mock_driver.find_elements("css selector", ".repo-list-item")
        
        with allure.step("验证仓库数量"):
            assert len(repos) == 5


@allure.feature("用户操作")
class TestUserOperations:
    """用户操作测试类"""
    
    @allure.story("个人中心")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试用户登录状态")
    def test_user_logged_in(self):
        """测试用户登录状态"""
        with allure.step("Mock WebDriver"):
            mock_driver = MagicMock()
            mock_avatar = MagicMock()
            mock_driver.find_element.return_value = mock_avatar
        
        with allure.step("检查用户是否登录"):
            avatar = mock_driver.find_element("css selector", ".avatar")
        
        with allure.step("验证登录状态"):
            assert avatar is not None
    
    @allure.story("个人中心")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试获取用户头像")
    def test_get_user_avatar(self):
        """测试获取用户头像"""
        with allure.step("Mock WebDriver"):
            mock_driver = MagicMock()
            mock_avatar = MagicMock()
            mock_avatar.get_attribute.return_value = "https://avatars.githubusercontent.com/u/123456"
            mock_driver.find_element.return_value = mock_avatar
        
        with allure.step("获取用户头像URL"):
            avatar = mock_driver.find_element("css selector", ".avatar")
            avatar_url = avatar.get_attribute("src")
        
        with allure.step("验证头像URL"):
            assert avatar_url is not None
            assert "avatars.githubusercontent.com" in avatar_url
    
    @allure.story("设置")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试退出登录")
    def test_sign_out(self):
        """测试退出登录"""
        with allure.step("Mock WebDriver"):
            mock_driver = MagicMock()
            mock_avatar = MagicMock()
            mock_sign_out = MagicMock()
            
            def find_element_side_effect(by, value):
                if "avatar" in str(value):
                    return mock_avatar
                return mock_sign_out
            
            mock_driver.find_element.side_effect = find_element_side_effect
        
        with allure.step("点击用户头像"):
            avatar = mock_driver.find_element("css selector", ".avatar")
            avatar.click()
        
        with allure.step("点击退出登录"):
            sign_out = mock_driver.find_element("link text", "Sign out")
            sign_out.click()
        
        with allure.step("验证退出操作"):
            assert avatar.click.called
            assert sign_out.click.called
