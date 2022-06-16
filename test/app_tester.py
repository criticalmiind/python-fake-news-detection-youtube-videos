import time
import datetime
import json
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ExpectedCondition


class Tester:
    def __init__(self):
        super().__init__()
        self.init_tester()
        self.url = "http://localhost:8000/"
        self.time_delay = 0.5

    '''
    -- Initialize the selenium firefox driver
    '''

    def init_tester(self):
        try:
            self.driver = webdriver.Firefox(executable_path="geckodriver.exe")
        except:
            raise Exception('Could not connect to the browser.')

    '''
    --
    '''

    def login_test(self, uname, pwd, testName='Test login'):
        log_data = {'test_name': testName, 'messages': [], 'error': []}

        try:
            header_login_btn = self.driver.find_element_by_id('header_login')
            header_login_btn.click()

            login_username = self.driver.find_element_by_id('id_username')
            login_password = self.driver.find_element_by_id('id_password')

            login_username.clear()
            login_password.clear()

            login_username.send_keys(uname)
            login_password.send_keys(pwd)

            login_btn = self.driver.find_element_by_id('login_pg')
            login_btn.click()
            log_data['messages'].append("Successful login")
        except NoSuchElementException as e:
            log_data['error'].append("Test failed")
        except Exception as e:
            log_data['error'].append(str(e))
        self.logger(log_data)

    '''
    --
    '''

    def link_test(self, link, testName='Test video link'):
        log_data = {'test_name': testName, 'messages': [], 'error': []}

        try:
            url_input = self.driver.find_element_by_id('url_input')
            url_input.clear()
            url_input.send_keys(link)
            search_btn = self.driver.find_element_by_id('search_btn')
            search_btn.click()

            time.sleep(1)

            if (self.driver.current_url == self.url + 'video'):
                log_data['messages'].append("Successful video input")
            else:
                log_data['messages'].append("Video did not load")
        except NoSuchElementException as e:
            log_data['error'].append("Test failed")
        except Exception as e:
            log_data['error'].append(str(e))
        self.logger(log_data)

    '''
    --
    '''

    def save_fact(self, testName='Test fact saving'):
        log_data = {'test_name': testName, 'messages': [], 'error': []}

        try:
            waiting = WebDriverWait(self.driver, 120).until(ExpectedCondition.presence_of_element_located((By.ID, "save_btn")))
            save_btn = self.driver.find_element_by_id('save_btn')
            save_btn.click()
            time.sleep(self.time_delay)

            ok_btn = self.driver.find_element_by_class_name('swal2-confirm')
            ok_btn.click()


            log_data['messages'].append("Successful fact save")

        except NoSuchElementException as e:
            log_data['error'].append("Test failed")
        except Exception as e:
            log_data['error'].append(str(e))
        self.logger(log_data)

    '''
    --
    '''
    def list_facts(self, testName='Check saved facts'):
        log_data = {'test_name': testName, 'messages': [], 'error': []}

        try:
            facts_btn = self.driver.find_element_by_id('saved_facts')
            facts_btn.click()
            time.sleep(self.time_delay)

            if (self.driver.current_url == self.url + 'savedFacts'):
                log_data['messages'].append("Successfully load saved facts")
            else:
                log_data['messages'].append("Saved facts not loading")
        except NoSuchElementException as e:
            log_data['error'].append("Test failed")
        except Exception as e:
            log_data['error'].append(str(e))
        self.logger(log_data)

    '''
    --
    '''
    def delete_fact(self, testName='Delete Fact'):
        log_data = {'test_name': testName, 'messages': [], 'error': []}

        try:
            delete_btn = self.driver.find_element_by_id('delete_btn')
            delete_btn.click()
            time.sleep(self.time_delay)

            if (self.driver.current_url == self.url + 'savedFacts'):
                log_data['messages'].append("Successfully deleted fact")
            else:
                log_data['messages'].append("Fact deletion failed")
        except NoSuchElementException as e:
            log_data['error'].append("Test failed")
        except Exception as e:
            log_data['error'].append(str(e))
        self.logger(log_data)

    '''
    -- Enables the logging of test results to a file
    '''

    def logger(self, log_data):
        try:
            with open("login_test_logs.txt", "a") as file:
                file.write(
                    "--------------------------------------\nTest Name:\n- ")
                file.write(log_data['test_name'])
                file.write(f"\nMessages:")
                if (len(log_data['messages']) > 0):
                    for msg in log_data['messages']:
                        file.write(f"\n- Message - {msg}")
                file.write(f"\nErrors: ")
                if (len(log_data['error']) > 0):
                    for err in log_data['error']:
                        file.write(f"\n- Error - {err}")
                else:
                    file.write(f"None")
                file.write('\n')
            file.close
        except:
            print("Couldn't write to file")

    '''
    -- Run all defined tests and log the results
    '''

    def test_runner(self):
        start = time.time()
        self.driver.get(self.url)

        '''
        -- TEST
        '''
        self.login_test('admin', 'Veritas123')
        self.link_test('https://www.youtube.com/watch?v=o2c_RrjCnXE')
        self.save_fact()
        self.list_facts()
        self.delete_fact()

        self.dispose()
        end = time.time()
        print(f'Execution time: {round(end-start,2)}s')

    '''
    -- Dispose the driver once all tests are completed
    '''

    def dispose(self):
        self.driver.close()


'''
-- Script runner section
'''


def main():
    tester = Tester()
    tester.test_runner()


if __name__ == '__main__':
    main()
