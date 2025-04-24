"""Tests for the system information plugin.

This module contains tests for the system information plugin functionality.

Version: 0.1.0
Created: 2025-04-22
"""

import os
import platform
import socket
import time
from unittest.mock import patch, MagicMock

import pytest
import psutil

from augment_adam.plugins.system_info import SystemInfoPlugin


@pytest.fixture
def plugin():
    """Create a system information plugin for testing."""
    return SystemInfoPlugin()


def test_plugin_init():
    """Test that the plugin initializes correctly."""
    plugin = SystemInfoPlugin(version="0.2.0")

    assert plugin.name == "system_info"
    assert plugin.description == "Plugin for system information operations"
    assert plugin.version == "0.2.0"


@patch('augment_adam.plugins.system_info.platform.system")
@patch('augment_adam.plugins.system_info.platform.node")
@patch('augment_adam.plugins.system_info.platform.release")
@patch('augment_adam.plugins.system_info.platform.version")
@patch('augment_adam.plugins.system_info.platform.machine")
@patch('augment_adam.plugins.system_info.platform.processor")
@patch('augment_adam.plugins.system_info.socket.gethostname")
@patch('augment_adam.plugins.system_info.socket.gethostbyname")
@patch('augment_adam.plugins.system_info.psutil.boot_time")
@patch('augment_adam.plugins.system_info.time.time")
def test_get_system_info(
    mock_time, mock_boot_time, mock_gethostbyname, mock_gethostname,
    mock_processor, mock_machine, mock_version, mock_release, mock_node, mock_system,
    plugin
):
    """Test getting system information."""
    # Set up the mocks
    mock_system.return_value = "Linux"
    mock_node.return_value = "test-node"
    mock_release.return_value = "5.10.0"
    mock_version.return_value = "#1 SMP Debian 5.10.0-10 (2021-06-15)"
    mock_machine.return_value = "x86_64"
    mock_processor.return_value = "x86_64"
    mock_gethostname.return_value = "test-host"
    mock_gethostbyname.return_value = "127.0.0.1"
    mock_boot_time.return_value = 1000
    mock_time.return_value = 2000

    # Get system information
    info = plugin.get_system_info()

    # Check the information
    assert info["system"] == "Linux"
    assert info["node"] == "test-node"
    assert info["release"] == "5.10.0"
    assert info["version"] == "#1 SMP Debian 5.10.0-10 (2021-06-15)"
    assert info["machine"] == "x86_64"
    assert info["processor"] == "x86_64"
    assert info["hostname"] == "test-host"
    assert info["ip_address"] == "127.0.0.1"
    assert info["uptime"] == 1000  # 2000 - 1000
    assert info["timestamp"] == 2000
    assert "python" in info
    assert "environment" in info


@patch('augment_adam.plugins.system_info.psutil.cpu_count")
@patch('augment_adam.plugins.system_info.psutil.cpu_freq")
@patch('augment_adam.plugins.system_info.psutil.cpu_percent")
@patch('augment_adam.plugins.system_info.psutil.cpu_times")
@patch('augment_adam.plugins.system_info.psutil.cpu_stats")
@patch('augment_adam.plugins.system_info.time.time")
def test_get_cpu_info(
    mock_time, mock_cpu_stats, mock_cpu_times, mock_cpu_percent,
    mock_cpu_freq, mock_cpu_count, plugin
):
    """Test getting CPU information."""
    # Set up the mocks
    mock_cpu_count.side_effect = lambda logical: 4 if logical else 2

    mock_freq = MagicMock()
    mock_freq.max = 3000
    mock_freq.current = 2000
    mock_cpu_freq.return_value = mock_freq

    # Fix the mock for cpu_percent to handle the percpu parameter correctly
    mock_cpu_percent.side_effect = lambda percpu=False: [
        10, 20, 30, 40] if percpu else 25

    mock_times = MagicMock()
    mock_times.user = 1000
    mock_times.system = 500
    mock_times.idle = 2000
    mock_cpu_times.return_value = mock_times

    mock_stats = MagicMock()
    mock_stats.ctx_switches = 1000
    mock_stats.interrupts = 500
    mock_stats.soft_interrupts = 200
    mock_stats.syscalls = 5000
    mock_cpu_stats.return_value = mock_stats

    mock_time.return_value = 2000

    # Get CPU information
    info = plugin.get_cpu_info()

    # Check the information
    assert "physical_cores" in info
    assert info["physical_cores"] == 2
    assert info["total_cores"] == 4
    assert info["max_frequency"] == 3000
    assert info["current_frequency"] == 2000
    assert info["usage_per_core"] == [10, 20, 30, 40]
    assert info["total_usage"] == 25
    assert info["timestamp"] == 2000

    assert info["times"]["user"] == 1000
    assert info["times"]["system"] == 500
    assert info["times"]["idle"] == 2000

    assert info["stats"]["ctx_switches"] == 1000
    assert info["stats"]["interrupts"] == 500
    assert info["stats"]["soft_interrupts"] == 200
    assert info["stats"]["syscalls"] == 5000


@patch('augment_adam.plugins.system_info.psutil.virtual_memory")
@patch('augment_adam.plugins.system_info.psutil.swap_memory")
@patch('augment_adam.plugins.system_info.time.time")
def test_get_memory_info(mock_time, mock_swap_memory, mock_virtual_memory, plugin):
    """Test getting memory information."""
    # Set up the mocks
    mock_virtual = MagicMock()
    mock_virtual.total = 16000000000
    mock_virtual.available = 8000000000
    mock_virtual.used = 8000000000
    mock_virtual.free = 8000000000
    mock_virtual.percent = 50
    mock_virtual_memory.return_value = mock_virtual

    mock_swap = MagicMock()
    mock_swap.total = 8000000000
    mock_swap.used = 1000000000
    mock_swap.free = 7000000000
    mock_swap.percent = 12.5
    mock_swap_memory.return_value = mock_swap

    mock_time.return_value = 2000

    # Get memory information
    info = plugin.get_memory_info()

    # Check the information
    assert info["virtual"]["total"] == 16000000000
    assert info["virtual"]["available"] == 8000000000
    assert info["virtual"]["used"] == 8000000000
    assert info["virtual"]["free"] == 8000000000
    assert info["virtual"]["percent"] == 50

    assert info["swap"]["total"] == 8000000000
    assert info["swap"]["used"] == 1000000000
    assert info["swap"]["free"] == 7000000000
    assert info["swap"]["percent"] == 12.5

    assert info["timestamp"] == 2000


@patch('augment_adam.plugins.system_info.psutil.disk_partitions")
@patch('augment_adam.plugins.system_info.psutil.disk_usage")
@patch('augment_adam.plugins.system_info.psutil.disk_io_counters")
@patch('augment_adam.plugins.system_info.time.time")
def test_get_disk_info(
    mock_time, mock_disk_io_counters, mock_disk_usage, mock_disk_partitions, plugin
):
    """Test getting disk information."""
    # Set up the mocks
    mock_partition1 = MagicMock()
    mock_partition1.device = "/dev/sda1"
    mock_partition1.mountpoint = "/"
    mock_partition1.fstype = "ext4"
    mock_partition1.opts = "rw,relatime"

    mock_partition2 = MagicMock()
    mock_partition2.device = "/dev/sda2"
    mock_partition2.mountpoint = "/home"
    mock_partition2.fstype = "ext4"
    mock_partition2.opts = "rw,relatime"

    mock_disk_partitions.return_value = [mock_partition1, mock_partition2]

    mock_usage1 = MagicMock()
    mock_usage1.total = 100000000000
    mock_usage1.used = 50000000000
    mock_usage1.free = 50000000000
    mock_usage1.percent = 50

    mock_usage2 = MagicMock()
    mock_usage2.total = 200000000000
    mock_usage2.used = 100000000000
    mock_usage2.free = 100000000000
    mock_usage2.percent = 50

    mock_disk_usage.side_effect = lambda mountpoint: mock_usage1 if mountpoint == "/" else mock_usage2

    mock_io = MagicMock()
    mock_io.read_count = 1000
    mock_io.write_count = 500
    mock_io.read_bytes = 10000000
    mock_io.write_bytes = 5000000
    mock_io.read_time = 1000
    mock_io.write_time = 500
    mock_disk_io_counters.return_value = mock_io

    mock_time.return_value = 2000

    # Get disk information
    info = plugin.get_disk_info()

    # Check the information
    assert len(info["partitions"]) == 2

    assert info["partitions"][0]["device"] == "/dev/sda1"
    assert info["partitions"][0]["mountpoint"] == "/"
    assert info["partitions"][0]["fstype"] == "ext4"
    assert info["partitions"][0]["opts"] == "rw,relatime"
    assert info["partitions"][0]["total"] == 100000000000
    assert info["partitions"][0]["used"] == 50000000000
    assert info["partitions"][0]["free"] == 50000000000
    assert info["partitions"][0]["percent"] == 50

    assert info["partitions"][1]["device"] == "/dev/sda2"
    assert info["partitions"][1]["mountpoint"] == "/home"
    assert info["partitions"][1]["fstype"] == "ext4"
    assert info["partitions"][1]["opts"] == "rw,relatime"
    assert info["partitions"][1]["total"] == 200000000000
    assert info["partitions"][1]["used"] == 100000000000
    assert info["partitions"][1]["free"] == 100000000000
    assert info["partitions"][1]["percent"] == 50

    assert info["io_stats"]["read_count"] == 1000
    assert info["io_stats"]["write_count"] == 500
    assert info["io_stats"]["read_bytes"] == 10000000
    assert info["io_stats"]["write_bytes"] == 5000000
    assert info["io_stats"]["read_time"] == 1000
    assert info["io_stats"]["write_time"] == 500

    assert info["timestamp"] == 2000


@patch('augment_adam.plugins.system_info.psutil.net_if_addrs")
@patch('augment_adam.plugins.system_info.psutil.net_io_counters")
@patch('augment_adam.plugins.system_info.psutil.net_connections")
@patch('augment_adam.plugins.system_info.time.time")
def test_get_network_info(
    mock_time, mock_net_connections, mock_net_io_counters, mock_net_if_addrs, plugin
):
    """Test getting network information."""
    # Set up the mocks
    mock_addr1 = MagicMock()
    mock_addr1.family = "AF_INET"
    mock_addr1.address = "192.168.1.100"
    mock_addr1.netmask = "255.255.255.0"
    mock_addr1.broadcast = "192.168.1.255"

    mock_addr2 = MagicMock()
    mock_addr2.family = "AF_INET6"
    mock_addr2.address = "fe80::1"
    mock_addr2.netmask = None
    mock_addr2.broadcast = None

    mock_net_if_addrs.return_value = {
        "eth0": [mock_addr1, mock_addr2],
    }

    mock_io = MagicMock()
    mock_io.bytes_sent = 1000000
    mock_io.bytes_recv = 2000000
    mock_io.packets_sent = 1000
    mock_io.packets_recv = 2000
    mock_io.errin = 0
    mock_io.errout = 0
    mock_io.dropin = 0
    mock_io.dropout = 0

    mock_net_io_counters.return_value = {
        "eth0": mock_io,
    }

    mock_conn = MagicMock()
    mock_conn.fd = 3
    mock_conn.family = "AF_INET"
    mock_conn.type = "SOCK_STREAM"
    mock_conn.laddr = MagicMock(ip="127.0.0.1", port=8080)
    mock_conn.raddr = MagicMock(ip="192.168.1.1", port=12345)
    mock_conn.status = "ESTABLISHED"
    mock_conn.pid = 1234

    mock_net_connections.return_value = [mock_conn]

    mock_time.return_value = 2000

    # Get network information
    info = plugin.get_network_info()

    # Check the information
    assert len(info["interfaces"]) == 1
    assert info["interfaces"][0]["name"] == "eth0"
    assert len(info["interfaces"][0]["addresses"]) == 2

    assert info["interfaces"][0]["addresses"][0]["family"] == "AF_INET"
    assert info["interfaces"][0]["addresses"][0]["address"] == "192.168.1.100"
    assert info["interfaces"][0]["addresses"][0]["netmask"] == "255.255.255.0"
    assert info["interfaces"][0]["addresses"][0]["broadcast"] == "192.168.1.255"

    assert info["interfaces"][0]["addresses"][1]["family"] == "AF_INET6"
    assert info["interfaces"][0]["addresses"][1]["address"] == "fe80::1"

    assert "eth0" in info["io_stats"]
    assert info["io_stats"]["eth0"]["bytes_sent"] == 1000000
    assert info["io_stats"]["eth0"]["bytes_recv"] == 2000000
    assert info["io_stats"]["eth0"]["packets_sent"] == 1000
    assert info["io_stats"]["eth0"]["packets_recv"] == 2000

    assert len(info["connections"]) == 1
    assert info["connections"][0]["fd"] == 3
    assert info["connections"][0]["family"] == "AF_INET"
    assert info["connections"][0]["type"] == "SOCK_STREAM"
    assert info["connections"][0]["laddr"] == "127.0.0.1:8080"
    assert info["connections"][0]["raddr"] == "192.168.1.1:12345"
    assert info["connections"][0]["status"] == "ESTABLISHED"
    assert info["connections"][0]["pid"] == 1234

    assert info["timestamp"] == 2000


@patch('augment_adam.plugins.system_info.psutil.pid_exists")
@patch('augment_adam.plugins.system_info.psutil.Process")
@patch('augment_adam.plugins.system_info.time.time")
def test_get_process_info(mock_time, mock_process, mock_pid_exists, plugin):
    """Test getting process information."""
    # Set up the mocks
    mock_pid_exists.return_value = True

    mock_proc = MagicMock()
    mock_proc.pid = 1234
    mock_proc.name.return_value = "test-process"
    mock_proc.status.return_value = "running"
    mock_proc.create_time.return_value = 1000
    mock_proc.username.return_value = "testuser"
    mock_proc.terminal.return_value = "/dev/pts/0"
    mock_proc.cmdline.return_value = ["python", "test.py"]
    mock_proc.cwd.return_value = "/home/testuser"
    mock_proc.exe.return_value = "/usr/bin/python"
    mock_proc.cpu_percent.return_value = 10
    mock_proc.memory_percent.return_value = 5

    mock_memory = MagicMock()
    mock_memory.rss = 100000000
    mock_memory.vms = 200000000
    mock_proc.memory_info.return_value = mock_memory

    mock_proc.num_threads.return_value = 5

    mock_io = MagicMock()
    mock_io.read_count = 1000
    mock_io.write_count = 500
    mock_io.read_bytes = 10000000
    mock_io.write_bytes = 5000000
    mock_proc.io_counters.return_value = mock_io

    mock_conn = MagicMock()
    mock_conn.fd = 3
    mock_conn.family = "AF_INET"
    mock_conn.type = "SOCK_STREAM"
    mock_conn.laddr = MagicMock(ip="127.0.0.1", port=8080)
    mock_conn.raddr = MagicMock(ip="192.168.1.1", port=12345)
    mock_conn.status = "ESTABLISHED"
    mock_proc.connections.return_value = [mock_conn]

    mock_process.return_value = mock_proc

    mock_time.return_value = 2000

    # Get process information
    info = plugin.get_process_info(1234)

    # Check the information
    assert info["pid"] == 1234
    assert info["name"] == "test-process"
    assert info["status"] == "running"
    assert info["created"] == 1000
    assert info["username"] == "testuser"
    assert info["terminal"] == "/dev/pts/0"
    assert info["cmdline"] == ["python", "test.py"]
    assert info["cwd"] == "/home/testuser"
    assert info["exe"] == "/usr/bin/python"
    assert info["cpu_percent"] == 10
    assert info["memory_percent"] == 5
    assert info["memory_info"]["rss"] == 100000000
    assert info["memory_info"]["vms"] == 200000000
    assert info["num_threads"] == 5

    assert info["io_counters"]["read_count"] == 1000
    assert info["io_counters"]["write_count"] == 500
    assert info["io_counters"]["read_bytes"] == 10000000
    assert info["io_counters"]["write_bytes"] == 5000000

    assert len(info["connections"]) == 1
    assert info["connections"][0]["fd"] == 3
    assert info["connections"][0]["family"] == "AF_INET"
    assert info["connections"][0]["type"] == "SOCK_STREAM"
    assert info["connections"][0]["laddr"] == "127.0.0.1:8080"
    assert info["connections"][0]["raddr"] == "192.168.1.1:12345"
    assert info["connections"][0]["status"] == "ESTABLISHED"

    assert info["timestamp"] == 2000


@patch('augment_adam.plugins.system_info.psutil.pid_exists")
def test_get_process_info_nonexistent(mock_pid_exists, plugin):
    """Test getting information for a non-existent process."""
    # Set up the mocks
    mock_pid_exists.return_value = False

    # Get process information
    info = plugin.get_process_info(9999)

    # Check the information
    assert "error" in info
    assert "does not exist" in info["error"]


@patch('augment_adam.plugins.system_info.SystemInfoPlugin.get_system_info")
@patch('augment_adam.plugins.system_info.SystemInfoPlugin.get_cpu_info")
@patch('augment_adam.plugins.system_info.SystemInfoPlugin.get_memory_info")
@patch('augment_adam.plugins.system_info.SystemInfoPlugin.get_disk_info")
@patch('augment_adam.plugins.system_info.SystemInfoPlugin.get_network_info")
@patch('augment_adam.plugins.system_info.time.time")
def test_get_all_info(
    mock_time, mock_network, mock_disk, mock_memory, mock_cpu, mock_system, plugin
):
    """Test getting all system information."""
    # Set up the mocks
    mock_system.return_value = {"system": "test"}
    mock_cpu.return_value = {"cpu": "test"}
    mock_memory.return_value = {"memory": "test"}
    mock_disk.return_value = {"disk": "test"}
    mock_network.return_value = {"network": "test"}
    mock_time.return_value = 2000

    # Get all information
    info = plugin.get_all_info()

    # Check the information
    assert info["system"] == {"system": "test"}
    assert info["cpu"] == {"cpu": "test"}
    assert info["memory"] == {"memory": "test"}
    assert info["disk"] == {"disk": "test"}
    assert info["network"] == {"network": "test"}
    assert info["timestamp"] == 2000


@patch('augment_adam.plugins.system_info.SystemInfoPlugin.get_system_info")
@patch('augment_adam.plugins.system_info.SystemInfoPlugin.get_cpu_info")
@patch('augment_adam.plugins.system_info.SystemInfoPlugin.get_memory_info")
@patch('augment_adam.plugins.system_info.SystemInfoPlugin.get_disk_info")
@patch('augment_adam.plugins.system_info.SystemInfoPlugin.get_network_info")
@patch('augment_adam.plugins.system_info.SystemInfoPlugin.get_process_info")
@patch('augment_adam.plugins.system_info.SystemInfoPlugin.get_all_info")
def test_execute(
    mock_all, mock_process, mock_network, mock_disk, mock_memory, mock_cpu, mock_system, plugin
):
    """Test executing the plugin with different actions."""
    # Set up the mocks
    mock_system.return_value = {"system": "test"}
    mock_cpu.return_value = {"cpu": "test"}
    mock_memory.return_value = {"memory": "test"}
    mock_disk.return_value = {"disk": "test"}
    mock_network.return_value = {"network": "test"}
    mock_process.return_value = {"process": "test"}
    mock_all.return_value = {"all": "test"}

    # Test different actions
    assert plugin.execute(action="system") == {"system": "test"}
    assert plugin.execute(action="cpu") == {"cpu": "test"}
    assert plugin.execute(action="memory") == {"memory": "test"}
    assert plugin.execute(action="disk") == {"disk": "test"}
    assert plugin.execute(action="network") == {"network": "test"}
    assert plugin.execute(action="process", pid=1234) == {"process": "test"}
    assert plugin.execute(action="all") == {"all": "test"}

    # Test invalid action
    result = plugin.execute(action="invalid")
    assert "error" in result
    assert "Unknown action" in result["error"]

    # Test missing PID for process action
    result = plugin.execute(action="process")
    assert "error" in result
    assert "PID is required" in result["error"]
