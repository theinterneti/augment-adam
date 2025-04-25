"""System information plugin for the Augment Adam assistant.

This module provides a plugin for retrieving system information,
including hardware, operating system, and resource usage.

Version: 0.1.0
Created: 2025-04-22
"""

from typing import Dict, Any, List, Optional, Union
import logging
import os
import platform
import socket
import time
import json
import subprocess
from datetime import datetime

import psutil

from augment_adam.plugins.base import Plugin

logger = logging.getLogger(__name__)


class SystemInfoPlugin(Plugin):
    """Plugin for system information operations.
    
    This plugin provides functionality for retrieving system information,
    including hardware, operating system, and resource usage.
    
    Attributes:
        name: The name of the plugin.
        description: A description of the plugin.
        version: The version of the plugin.
    """
    
    def __init__(
        self,
        version: str = "0.1.0",
    ):
        """Initialize the system information plugin.
        
        Args:
            version: The version of the plugin.
        """
        super().__init__(
            name="system_info",
            description="Plugin for system information operations",
            version=version,
        )
        
        logger.info("Initialized system information plugin")
    
    def execute(
        self,
        action: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """Execute a system information operation.
        
        Args:
            action: The action to perform (system, cpu, memory, disk, network, process).
            **kwargs: Additional arguments for the action.
            
        Returns:
            The result of the operation.
        """
        try:
            if action == "system":
                return self.get_system_info()
            elif action == "cpu":
                return self.get_cpu_info()
            elif action == "memory":
                return self.get_memory_info()
            elif action == "disk":
                return self.get_disk_info()
            elif action == "network":
                return self.get_network_info()
            elif action == "process":
                pid = kwargs.get("pid")
                if pid is None:
                    return {"error": "PID is required for process information"}
                return self.get_process_info(pid)
            elif action == "all":
                return self.get_all_info()
            else:
                error_msg = f"Unknown action: {action}"
                logger.error(error_msg)
                return {"error": error_msg}
        
        except Exception as e:
            error_msg = f"Error performing {action}: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get general system information.
        
        Returns:
            General system information.
        """
        try:
            # Get system information
            info = {
                "system": platform.system(),
                "node": platform.node(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "hostname": socket.gethostname(),
                "ip_address": socket.gethostbyname(socket.gethostname()),
                "uptime": int(time.time() - psutil.boot_time()),
                "timestamp": int(time.time()),
            }
            
            # Get Python information
            info["python"] = {
                "version": platform.python_version(),
                "implementation": platform.python_implementation(),
                "compiler": platform.python_compiler(),
                "build": platform.python_build(),
            }
            
            # Get environment variables (filtered)
            safe_env_vars = ["PATH", "PYTHONPATH", "HOME", "USER", "SHELL", "LANG", "TERM"]
            env_vars = {}
            for var in safe_env_vars:
                if var in os.environ:
                    env_vars[var] = os.environ[var]
            
            info["environment"] = env_vars
            
            return info
        
        except Exception as e:
            error_msg = f"Error getting system information: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information.
        
        Returns:
            CPU information.
        """
        try:
            # Get CPU information
            info = {
                "physical_cores": psutil.cpu_count(logical=False),
                "total_cores": psutil.cpu_count(logical=True),
                "max_frequency": psutil.cpu_freq().max if psutil.cpu_freq() else None,
                "current_frequency": psutil.cpu_freq().current if psutil.cpu_freq() else None,
                "usage_per_core": [percentage for percentage in psutil.cpu_percent(percpu=True)],
                "total_usage": psutil.cpu_percent(),
                "timestamp": int(time.time()),
            }
            
            # Get CPU times
            cpu_times = psutil.cpu_times()
            info["times"] = {
                "user": cpu_times.user,
                "system": cpu_times.system,
                "idle": cpu_times.idle,
            }
            
            # Get CPU stats
            cpu_stats = psutil.cpu_stats()
            info["stats"] = {
                "ctx_switches": cpu_stats.ctx_switches,
                "interrupts": cpu_stats.interrupts,
                "soft_interrupts": cpu_stats.soft_interrupts,
                "syscalls": cpu_stats.syscalls,
            }
            
            return info
        
        except Exception as e:
            error_msg = f"Error getting CPU information: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory information.
        
        Returns:
            Memory information.
        """
        try:
            # Get virtual memory information
            virtual_memory = psutil.virtual_memory()
            info = {
                "virtual": {
                    "total": virtual_memory.total,
                    "available": virtual_memory.available,
                    "used": virtual_memory.used,
                    "free": virtual_memory.free,
                    "percent": virtual_memory.percent,
                },
                "timestamp": int(time.time()),
            }
            
            # Get swap memory information
            swap_memory = psutil.swap_memory()
            info["swap"] = {
                "total": swap_memory.total,
                "used": swap_memory.used,
                "free": swap_memory.free,
                "percent": swap_memory.percent,
            }
            
            return info
        
        except Exception as e:
            error_msg = f"Error getting memory information: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def get_disk_info(self) -> Dict[str, Any]:
        """Get disk information.
        
        Returns:
            Disk information.
        """
        try:
            # Get disk partitions
            partitions = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    partitions.append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "opts": partition.opts,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": usage.percent,
                    })
                except PermissionError:
                    # Skip partitions that can't be accessed
                    continue
            
            # Get disk I/O statistics
            io_counters = psutil.disk_io_counters()
            io_stats = {
                "read_count": io_counters.read_count,
                "write_count": io_counters.write_count,
                "read_bytes": io_counters.read_bytes,
                "write_bytes": io_counters.write_bytes,
                "read_time": io_counters.read_time,
                "write_time": io_counters.write_time,
            }
            
            return {
                "partitions": partitions,
                "io_stats": io_stats,
                "timestamp": int(time.time()),
            }
        
        except Exception as e:
            error_msg = f"Error getting disk information: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get network information.
        
        Returns:
            Network information.
        """
        try:
            # Get network interfaces
            interfaces = []
            for interface, addresses in psutil.net_if_addrs().items():
                interface_info = {
                    "name": interface,
                    "addresses": [],
                }
                
                for address in addresses:
                    addr_info = {
                        "family": str(address.family),
                        "address": address.address,
                        "netmask": address.netmask,
                        "broadcast": address.broadcast,
                    }
                    interface_info["addresses"].append(addr_info)
                
                interfaces.append(interface_info)
            
            # Get network I/O statistics
            io_counters = psutil.net_io_counters(pernic=True)
            io_stats = {}
            
            for interface, counters in io_counters.items():
                io_stats[interface] = {
                    "bytes_sent": counters.bytes_sent,
                    "bytes_recv": counters.bytes_recv,
                    "packets_sent": counters.packets_sent,
                    "packets_recv": counters.packets_recv,
                    "errin": counters.errin,
                    "errout": counters.errout,
                    "dropin": counters.dropin,
                    "dropout": counters.dropout,
                }
            
            # Get network connections
            connections = []
            for conn in psutil.net_connections(kind="inet"):
                conn_info = {
                    "fd": conn.fd,
                    "family": str(conn.family),
                    "type": str(conn.type),
                    "laddr": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                    "raddr": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                    "status": conn.status,
                    "pid": conn.pid,
                }
                connections.append(conn_info)
            
            return {
                "interfaces": interfaces,
                "io_stats": io_stats,
                "connections": connections,
                "timestamp": int(time.time()),
            }
        
        except Exception as e:
            error_msg = f"Error getting network information: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def get_process_info(self, pid: int) -> Dict[str, Any]:
        """Get information about a specific process.
        
        Args:
            pid: The process ID.
            
        Returns:
            Process information.
        """
        try:
            # Check if the process exists
            if not psutil.pid_exists(pid):
                return {"error": f"Process with PID {pid} does not exist"}
            
            # Get process information
            process = psutil.Process(pid)
            
            info = {
                "pid": process.pid,
                "name": process.name(),
                "status": process.status(),
                "created": process.create_time(),
                "username": process.username(),
                "terminal": process.terminal(),
                "cmdline": process.cmdline(),
                "cwd": process.cwd(),
                "exe": process.exe(),
                "cpu_percent": process.cpu_percent(),
                "memory_percent": process.memory_percent(),
                "memory_info": {
                    "rss": process.memory_info().rss,
                    "vms": process.memory_info().vms,
                },
                "num_threads": process.num_threads(),
                "timestamp": int(time.time()),
            }
            
            # Get process I/O counters
            try:
                io_counters = process.io_counters()
                info["io_counters"] = {
                    "read_count": io_counters.read_count,
                    "write_count": io_counters.write_count,
                    "read_bytes": io_counters.read_bytes,
                    "write_bytes": io_counters.write_bytes,
                }
            except psutil.AccessDenied:
                info["io_counters"] = "Access denied"
            
            # Get process connections
            try:
                connections = []
                for conn in process.connections():
                    conn_info = {
                        "fd": conn.fd,
                        "family": str(conn.family),
                        "type": str(conn.type),
                        "laddr": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                        "raddr": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                        "status": conn.status,
                    }
                    connections.append(conn_info)
                info["connections"] = connections
            except psutil.AccessDenied:
                info["connections"] = "Access denied"
            
            return info
        
        except Exception as e:
            error_msg = f"Error getting process information: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def get_all_info(self) -> Dict[str, Any]:
        """Get all system information.
        
        Returns:
            All system information.
        """
        return {
            "system": self.get_system_info(),
            "cpu": self.get_cpu_info(),
            "memory": self.get_memory_info(),
            "disk": self.get_disk_info(),
            "network": self.get_network_info(),
            "timestamp": int(time.time()),
        }
