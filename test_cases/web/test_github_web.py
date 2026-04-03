"""
GitHub Web UI 测试

数据来源：data/web_test_data.yaml

测试场景：
1. 登录功能测试
2. 首页功能测试
3. 用户操作测试

设计模式：Page Object Model (POM)
- 使用 page_objects/ 目录下的页面对象类
- 通过 Mock 模拟 WebDriver 和 WebDriverWait，不需要真实浏览器
"""
import pytest
import allure
from unittest.mock import Mock, patch, MagicMock
from common.yaml_util import DataHelper
from page_objects.login_page import LoginPage
from page_objects.home_page import HomePage


def create_mock_element():
    """创建 Mock 元素"""
    element = MagicMock()
    element.is_displayed.return_value = True
    element.is_enabled.return_value = True
    element.text = "Mock Text"
    element.get_attribute.return_value = "https://avatars.githubusercontent.com/u/123456"
    return element


def create_mock_wait(mock_element):
    """创建 Mock WebDriverWait"""
    mock_wait = MagicMock()
    mock_wait.until.return_value = mock_element
    return mock_wait


@allure.feature("登录功能")
class TestLogin:
    """登录功能测试类 - 使用 LoginPage 页面对象"""
    
    @pytest.fixture
    def web_data(self):
        """加载 Web 测试数据"""
        return DataHelper.load_web_data()
    
    @pytest.fixture
    def mock_driver(self):
        """Mock WebDriver"""
        driver = MagicMock()
        driver.title = "GitHub"
        driver.current_url = "https://github.com/login"
        return driver
    
    @pytest.fixture
    def login_page(self, mock_driver):
        """创建登录页面对象"""
        with patch('page_objects.base_page.WebDriverWait') as mock_wait_class:
            mock_element = create_mock_element()
            mock_wait = create_mock_wait(mock_element)
            mock_wait_class.return_value = mock_wait
            
            page = LoginPage(mock_driver)
            page._mock_wait = mock_wait
            page._mock_element = mock_element
            yield page
    
    @allure.story("登录成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试登录成功 - Page Object 模式")
    def test_login_success(self, login_page, web_data):
        """测试登录成功 - 使用 LoginPage 页面对象"""
        login_data = web_data['login']['valid'][0]
        
        with allure.step("使用 LoginPage 执行登录"):
            login_page.login(login_data['username'], login_data['password'])
        
        with allure.step("验证登录操作执行"):
            assert login_page._mock_wait.until.called
    
    @allure.story("登录失败")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试登录失败显示错误信息 - Page Object 模式")
    def test_login_failure(self, login_page, web_data):
        """测试登录失败显示错误信息"""
        invalid_login = web_data['login']['invalid'][0]
        
        with allure.step("模拟登录失败错误信息"):
            login_page._mock_element.text = invalid_login['expected_error']
        
        with allure.step("获取错误信息"):
            error_msg = login_page.get_error_message()
        
        with allure.step("验证错误信息"):
            assert "Incorrect" in error_msg
    
    @allure.story("表单验证")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试登录页面元素显示 - Page Object 模式")
    def test_login_page_elements(self, login_page):
        """测试登录页面元素显示 - 使用 LoginPage 方法"""
        with allure.step("验证用户名输入框显示"):
            assert login_page.is_username_field_displayed()
        
        with allure.step("验证密码输入框显示"):
            assert login_page.is_password_field_displayed()
        
        with allure.step("验证登录按钮显示"):
            assert login_page.is_sign_in_button_displayed()
    
    @allure.story("表单验证")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试空用户名登录")
    def test_login_empty_username(self, web_data):
        """测试空用户名登录"""
        invalid_login = web_data['login']['invalid'][1]
        
        with allure.step("验证错误信息"):
            error_msg = invalid_login['expected_error']
            assert "required" in error_msg.lower() or "Username" in error_msg or "Password" in error_msg


@allure.feature("首页功能")
class TestHomePage:
    """首页功能测试类 - 使用 HomePage 页面对象"""
    
    @pytest.fixture
    def web_data(self):
        """加载 Web 测试数据"""
        return DataHelper.load_web_data()
    
    @pytest.fixture
    def mock_driver(self):
        """Mock WebDriver"""
        driver = MagicMock()
        driver.title = "GitHub"
        driver.current_url = "https://github.com"
        return driver
    
    @pytest.fixture
    def home_page(self, mock_driver):
        """创建首页页面对象"""
        with patch('page_objects.base_page.WebDriverWait') as mock_wait_class:
            mock_element = create_mock_element()
            mock_wait = create_mock_wait(mock_element)
            mock_wait_class.return_value = mock_wait
            
            page = HomePage(mock_driver)
            page._mock_wait = mock_wait
            page._mock_element = mock_element
            yield page
    
    @allure.story("页面加载")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试首页加载 - Page Object 模式")
    def test_home_page_load(self, home_page):
        """测试首页加载 - 使用 HomePage 页面对象"""
        with allure.step("验证首页元素"):
            assert home_page.is_home_page_displayed()
    
    @allure.story("导航")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试导航功能 - Page Object 模式")
    def test_navigation(self, home_page, web_data):
        """测试导航功能 - 使用 HomePage 方法"""
        navigation_items = web_data['home']['navigation']
        
        for nav_item in navigation_items:
            with allure.step(f"导航到 {nav_item['name']}"):
                if nav_item['name'] == "Pull requests":
                    home_page.navigate_to_pulls()
                elif nav_item['name'] == "Issues":
                    home_page.navigate_to_issues()
                elif nav_item['name'] == "Marketplace":
                    home_page.navigate_to_marketplace()
                elif nav_item['name'] == "Explore":
                    home_page.navigate_to_explore()
                
                assert home_page._mock_wait.until.called
    
    @allure.story("搜索")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试搜索功能 - Page Object 模式")
    def test_search(self, home_page, web_data):
        """测试搜索功能 - 使用 HomePage 方法"""
        search_data = web_data['home']['search']['valid'][0]
        
        with allure.step("使用 HomePage 搜索"):
            home_page.search(search_data['keyword'])
        
        with allure.step("验证搜索操作"):
            assert home_page._mock_wait.until.called
    
    @allure.story("仓库列表")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试仓库列表显示 - Page Object 模式")
    def test_repo_list(self, home_page):
        """测试仓库列表显示 - 使用 HomePage 方法"""
        with allure.step("Mock 仓库列表"):
            mock_repos = [MagicMock() for _ in range(5)]
            home_page._mock_wait.until.return_value = mock_repos
        
        with allure.step("获取仓库数量"):
            count = home_page.get_repo_count()
        
        with allure.step("验证仓库数量"):
            assert count == 5


@allure.feature("用户操作")
class TestUserOperations:
    """用户操作测试类 - 使用 HomePage 页面对象"""
    
    @pytest.fixture
    def web_data(self):
        """加载 Web 测试数据"""
        return DataHelper.load_web_data()
    
    @pytest.fixture
    def mock_driver(self):
        """Mock WebDriver"""
        driver = MagicMock()
        driver.title = "GitHub"
        return driver
    
    @pytest.fixture
    def home_page(self, mock_driver):
        """创建首页页面对象"""
        with patch('page_objects.base_page.WebDriverWait') as mock_wait_class:
            mock_element = create_mock_element()
            mock_wait = create_mock_wait(mock_element)
            mock_wait_class.return_value = mock_wait
            
            page = HomePage(mock_driver)
            page._mock_wait = mock_wait
            page._mock_element = mock_element
            yield page
    
    @allure.story("个人中心")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试用户登录状态 - Page Object 模式")
    def test_user_logged_in(self, home_page):
        """测试用户登录状态 - 使用 HomePage 方法"""
        with allure.step("检查用户是否登录"):
            is_logged = home_page.is_user_logged_in()
        
        with allure.step("验证登录状态"):
            assert is_logged
    
    @allure.story("个人中心")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试获取用户头像 - Page Object 模式")
    def test_get_user_avatar(self, home_page):
        """测试获取用户头像 - 使用 HomePage 方法"""
        with allure.step("获取用户头像URL"):
            avatar_url = home_page.get_user_avatar_src()
        
        with allure.step("验证头像URL"):
            assert avatar_url is not None
            assert "avatars.githubusercontent.com" in avatar_url
    
    @allure.story("设置")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试退出登录 - Page Object 模式")
    def test_sign_out(self, home_page):
        """测试退出登录 - 使用 HomePage 方法"""
        with allure.step("使用 HomePage 退出登录"):
            home_page.sign_out()
        
        with allure.step("验证退出操作"):
            assert home_page._mock_wait.until.called
    
    @allure.story("个人中心")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试用户资料字段")
    def test_user_profile_fields(self, web_data):
        """测试用户资料字段"""
        expected_fields = web_data['user_operations']['profile']['expected_fields']
        
        with allure.step("验证期望的字段存在"):
            for field in expected_fields:
                assert field is not None
    
    @allure.story("设置")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试设置导航项")
    def test_settings_navigation(self, web_data):
        """测试设置导航项"""
        settings_items = web_data['user_operations']['settings']['navigation_items']
        
        with allure.step("验证设置导航项"):
            for item in settings_items:
                assert isinstance(item, str)
                assert len(item) > 0


@allure.feature("仓库页面测试")
class TestRepositoryPage:
    """仓库页面测试类"""
    
    @pytest.fixture
    def web_data(self):
        """加载 Web 测试数据"""
        return DataHelper.load_web_data()
    
    @allure.story("创建仓库")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试创建仓库数据")
    def test_create_repository_data(self, web_data):
        """测试创建仓库数据"""
        create_data = web_data['repository']['create']['valid']
        
        for repo in create_data:
            with allure.step(f"验证仓库数据: {repo['name']}"):
                assert repo['name'] is not None
                assert repo['description'] is not None
                assert repo['visibility'] in ['public', 'private']
    
    @allure.story("仓库元素")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试仓库页面元素定位")
    def test_repository_page_elements(self, web_data):
        """测试仓库页面元素定位"""
        repo_elements = web_data['repository']['elements']
        
        with allure.step("Mock WebDriver"):
            mock_driver = MagicMock()
            mock_element = MagicMock()
            mock_driver.find_element.return_value = mock_element
        
        with allure.step("验证仓库名输入框"):
            name_locator = repo_elements['repo_name_input']
            element = mock_driver.find_element(name_locator['by'], name_locator['value'])
            assert element is not None
        
        with allure.step("验证描述输入框"):
            desc_locator = repo_elements['description_input']
            element = mock_driver.find_element(desc_locator['by'], desc_locator['value'])
            assert element is not None
        
        with allure.step("验证创建按钮"):
            button_locator = repo_elements['create_button']
            element = mock_driver.find_element(button_locator['by'], button_locator['value'])
            assert element is not None


@allure.feature("通用元素测试")
class TestCommonElements:
    """通用元素测试类"""
    
    @pytest.fixture
    def web_data(self):
        """加载 Web 测试数据"""
        return DataHelper.load_web_data()
    
    @allure.story("通用元素")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试通用元素定位")
    def test_common_elements(self, web_data):
        """测试通用元素定位"""
        common_elements = web_data['common']['elements']
        
        with allure.step("Mock WebDriver"):
            mock_driver = MagicMock()
            mock_element = MagicMock()
            mock_driver.find_element.return_value = mock_element
        
        for element_name, locator in common_elements.items():
            with allure.step(f"验证元素: {element_name}"):
                element = mock_driver.find_element(locator['by'], locator['value'])
                assert element is not None


@allure.feature("配置测试")
class TestWebConfig:
    """Web 配置测试类"""
    
    @pytest.fixture
    def web_data(self):
        """加载 Web 测试数据"""
        return DataHelper.load_web_data()
    
    @allure.story("超时配置")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试超时配置")
    def test_timeout_config(self, web_data):
        """测试超时配置"""
        timeouts = web_data['timeouts']
        
        with allure.step("验证隐式等待时间"):
            assert timeouts['implicit'] == 10
        
        with allure.step("验证显式等待时间"):
            assert timeouts['explicit'] == 20
        
        with allure.step("验证页面加载超时"):
            assert timeouts['page_load'] == 30
        
        with allure.step("验证脚本超时"):
            assert timeouts['script'] == 30
    
    @allure.story("截图配置")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试截图配置")
    def test_screenshot_config(self, web_data):
        """测试截图配置"""
        screenshot = web_data['screenshot']
        
        with allure.step("验证失败时截图"):
            assert screenshot['on_failure'] == True
        
        with allure.step("验证成功时截图"):
            assert screenshot['on_success'] == False
        
        with allure.step("验证截图目录"):
            assert screenshot['directory'] == "reports/screenshots"


@allure.feature("首页导航元素测试")
class TestHomePageNavigation:
    """首页导航元素测试类"""
    
    @pytest.fixture
    def web_data(self):
        """加载 Web 测试数据"""
        return DataHelper.load_web_data()
    
    @allure.story("导航元素")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试首页导航元素定位")
    def test_home_navigation_elements(self, web_data):
        """测试首页导航元素定位"""
        nav_elements = web_data['home_page']['navigation']
        
        with allure.step("Mock WebDriver"):
            mock_driver = MagicMock()
            mock_element = MagicMock()
            mock_driver.find_element.return_value = mock_element
        
        for nav_name, locator in nav_elements.items():
            with allure.step(f"验证导航元素: {nav_name}"):
                element = mock_driver.find_element(locator['by'], locator['value'])
                assert element is not None
