from unittest import TestCase
import modules.run_cmd as run_cmd
import modules.config_mbox as mbox
import modules.config_stage as stage
import time
import os
import logging


class TestInitialize(TestCase):

    def test_run_cmd_os(self):
        command = 'date +"%s"'
        result = run_cmd.run_cmd_os(command)
        print(result)
        check_time = time.time()
        print(check_time)
        self.assertTrue(int(result) <= int(check_time))

    def test_run_cmd(self):
        command = 'date +"%s"'
        result = run_cmd.run_cmd(command)[0]
        print(result)
        check_time = time.time()
        print(check_time)
        self.assertTrue(int(result) <= int(check_time))

    def test_check_disk_space(self):
        stage.mount_system = "/"

        result = run_cmd.check_disk_space(init=False)
        print(result)
        self.assertEqual(result[2], -1)
        self.assertTrue(result[3] > 1)

        result = run_cmd.check_disk_space(init=True)
        print(result)
        self.assertTrue(result[2] > 1)
        self.assertTrue(result[3] > 1)

        result = run_cmd.check_disk_space(init=False)
        print(result)
        self.assertTrue(result[2] > 1)
        self.assertTrue(result[3] > 1)

        stage.mount_data = "/tmp"
        result = run_cmd.check_disk_space(init=True)
        print(result)
        self.assertTrue(result[0] > 0)
        self.assertTrue(result[1] > 0)
        self.assertTrue(result[1] > result[0])

    def test_file_logging(self):
        log_file = "/tmp/check_file_logging"
        log_string = "TEST LOGGING"
        if os.path.isfile(log_file):
            os.remove(log_file)
        run_cmd.file_logging(logging_string=log_string,logging_file=log_file)
        file = open(log_file, "r")
        content = file.read()
        print(content)
        file.close()
        self.assertTrue(log_string in content)

    def test_file_logging_init(self):
        log_file = "/tmp/check_file_logging"
        if os.path.isfile(log_file):
            os.remove(log_file)
        run_cmd.file_logging_init(logging_file=log_file)
        file = open(log_file, "r")
        content = file.read()
        print(content)
        file.close()
        self.assertTrue("Log level" in content)
        self.assertTrue("Load time" in content)

    def test_init_logging(self):
        log_file = "/tmp/check_file_logging"
        stage.logging_level = "INFO"
        stage.log_to_file = "yes"
        logging.shutdown()
        if os.path.isfile(log_file):
            os.remove(log_file)
        run_cmd.init_logging(log_string=log_file, logfilename=log_file)
        file = open(log_file, "r")
        content = file.read()
        print(content)
        file.close()
        self.assertTrue("Start - Log-Level INFO" in content)
        self.assertTrue(log_file in content)

    def test_ping(self):
        self.assertTrue(run_cmd.ping("localhost"))
        self.assertTrue(run_cmd.ping("127.0.0.1"))
        self.assertFalse(run_cmd.ping("192.168.0.0"))
        self.assertFalse(run_cmd.ping("this.domain.does.not.exist"))

    def test_check_internet_connect(self):
        old_log_file = mbox.log_connection
        mbox.log_connection = "/tmp/check_log"
        self.assertEqual(run_cmd.check_internet_connect(log_file=False), "CONNECTED")

        if os.path.isfile(mbox.log_connection):
            os.remove(mbox.log_connection)
        self.assertEqual(run_cmd.check_internet_connect(log_file=True), "CONNECTED")
        file = os.open(mbox.log_connection, os.O_RDWR)
        content = os.read(file, 100)
        os.close(file)
        self.assertEqual(content, "CONNECTED".encode('UTF-8'))
        mbox.log_connection = old_log_file

    def test_connection_status(self):
        old_log_file = mbox.log_connection
        old_auto_file = mbox.log_autohotspot
        mbox.log_connection = "/tmp/check_log"
        mbox.log_autohotspot = "/tmp/check_autohotspot"

        self.assertEqual(run_cmd.check_internet_connect(log_file=True), "CONNECTED")
        if os.path.isfile(mbox.log_autohotspot):
            os.remove(mbox.log_autohotspot)

        result = run_cmd.connection_status()
        print(result)
        self.assertEqual(result["CONNECT"], "CONNECTED")
        self.assertEqual(result["INTERNET"], "CONNECTED")
        self.assertEqual(result["TYPE"], "Autohotspot not activated")

        file = open(mbox.log_autohotspot, "w+")
        file.write("TEST-AUTOHOTSPOT")
        file.close()

        if os.path.isfile(mbox.log_connection):
            os.remove(mbox.log_connection)
        result = run_cmd.connection_status()
        print(result)
        self.assertEqual(result["CONNECT"], "Connection not checked yet")
        self.assertEqual(result["INTERNET"], "CONNECTED")
        self.assertEqual(result["TYPE"], "TEST-AUTOHOTSPOT")

        mbox.log_connection = old_log_file
        mbox.log_autohotspot = old_auto_file
