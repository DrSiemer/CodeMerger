import socket
import json
import logging
import uuid
import time
import struct
from ..core.utils import load_config

log = logging.getLogger("CodeMerger")

class UnrealClient:
    """
    A client for the Unreal Engine Python Remote Execution plugin.
    Implements the UDP Discovery -> TCP Command Protocol.
    """
    def __init__(self):
        self.command_socket = None
        self._is_connected = False
        self.config = load_config()
        self.multicast_group = '239.0.0.1'
        # Default UE discovery port is 6766
        self.discovery_port = self.config.get('unreal_port', 6766)

    def connect(self, timeout=5.0):
        """
        Discovers the Unreal Engine instance via UDP and establishes a TCP connection.
        Increased default timeout to 5.0s to allow for multiple ping attempts.
        """
        # Reload config to get latest port/enabled status
        self.config = load_config()
        if not self.config.get('unreal_integration_enabled', False):
            log.info("Unreal integration is disabled in settings.")
            return False

        self.discovery_port = self.config.get('unreal_port', 6766)
        self.disconnect()

        log.info(f"--- Starting Unreal Engine Discovery ---")
        log.info(f"Target: UDP Multicast {self.multicast_group}:{self.discovery_port}")
        log.info(f"Discovery Timeout: {timeout} seconds")
        
        target_ip, target_port = self._discover_engine_node(timeout)
        
        if not target_ip or not target_port:
            log.info("Unreal Engine discovery timed out. No 'pong' response received.")
            log.info("Troubleshooting: Check Firewall rules for 'UnrealEditor.exe' (UDP 6766).")
            return False

        log.info(f"Discovery Successful. Engine reported endpoint: {target_ip}:{target_port}")
        log.info(f"Attempting TCP connection...")

        try:
            self.command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.command_socket.settimeout(2.0) # TCP connect timeout
            self.command_socket.connect((target_ip, target_port))
            self._is_connected = True
            log.info("Successfully established TCP connection to Unreal Engine.")
            return True
        except Exception as e:
            log.error(f"Failed to connect to Unreal Engine TCP command port: {e}")
            self.disconnect()
            return False

    def _discover_engine_node(self, overall_timeout):
        """
        Sends multicast pings repeatedly until a pong is received or timeout occurs.
        """
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        
        try:
            # Allow reusing the address
            udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Set TTL to 1 (local subnet)
            udp_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
            
            # Enable Loopback
            udp_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
            
            # Short timeout for the socket recv
            socket_interval = 0.5
            udp_sock.settimeout(socket_interval)
            
            # Bind to default adapter
            udp_sock.bind(('', 0))
            log.info(f"UDP Socket bound successfully. Local socket name: {udp_sock.getsockname()}")
        except Exception as e:
            log.error(f"Socket setup error: {e}")
            return None, None

        my_uuid = str(uuid.uuid4())
        ping_msg = {
            "type": "ping",
            "id": my_uuid,
            "machine": socket.gethostname(),
            "user": "codemerger"
        }
        encoded_ping = json.dumps(ping_msg).encode('utf-8')

        start_time = time.time()
        attempt_count = 0
        
        try:
            while time.time() - start_time < overall_timeout:
                attempt_count += 1
                # 1. Send Ping
                try:
                    log.info(f"Sending Ping #{attempt_count}...")
                    udp_sock.sendto(encoded_ping, (self.multicast_group, self.discovery_port))
                except Exception as e:
                    log.warning(f"Failed to send UDP ping: {e}")

                # 2. Listen for Pong (for socket_interval seconds)
                try:
                    data, addr = udp_sock.recvfrom(4096)
                    log.info(f"Received {len(data)} bytes from {addr}")
                    
                    try:
                        decoded_str = data.decode('utf-8')
                        msg = json.loads(decoded_str)
                        log.info(f"Packet content: {msg}")
                        
                        if msg.get('type') == 'pong':
                            cmd_ip = msg.get('command_ip')
                            cmd_port = msg.get('command_port')
                            
                            # If UE reports 0.0.0.0 or empty, assume localhost
                            if not cmd_ip or cmd_ip == '0.0.0.0':
                                cmd_ip = '127.0.0.1'
                                
                            return cmd_ip, cmd_port
                        else:
                            log.info(f"Ignored packet (type is not 'pong').")
                            
                    except (json.JSONDecodeError, UnicodeDecodeError) as decode_err:
                        log.warning(f"Failed to decode packet: {decode_err}")
                        continue
                        
                except socket.timeout:
                    # Timeout on recv is expected, just loop back and ping again
                    # log.info("Socket timed out waiting for pong (normal behavior, retrying...)")
                    continue
                except Exception as e:
                    log.error(f"Unexpected error receiving UDP data: {e}")
                    continue
                    
        except Exception as e:
            log.warning(f"UDP Discovery Critical Error: {e}")
        finally:
            udp_sock.close()
        
        return None, None

    def disconnect(self):
        if self.command_socket:
            try:
                self.command_socket.close()
            except Exception:
                pass
        self.command_socket = None
        self._is_connected = False

    def is_connected(self):
        return self._is_connected

    def run_script(self, script_body):
        """
        Sends a script to the engine via the established TCP connection.
        """
        if not self._is_connected or not self.command_socket:
            return None

        message_id = str(uuid.uuid4())
        # Wrap script to ensure JSON output is isolated if UE prints logs
        safe_script = f"print('__JSON_START__');\n{script_body}\nprint('__JSON_END__')"
        
        payload = {
            "type": "command",
            "command": safe_script,
            "unattended": True,
            "id": message_id
        }
        
        try:
            payload_str = json.dumps(payload)
            self.command_socket.sendall(payload_str.encode('utf-8'))
            
            response_data = b""
            while True:
                chunk = self.command_socket.recv(4096)
                if not chunk: break
                response_data += chunk
                # Stop if we see the end of a JSON object structure corresponding to our ID
                if len(chunk) < 4096 and b"command_result" in response_data:
                    break

            decoded_response = response_data.decode('utf-8', errors='ignore')
            
            # Extract the actual output from the JSON wrapper(s)
            decoder = json.JSONDecoder()
            pos = 0
            while pos < len(decoded_response):
                try:
                    while pos < len(decoded_response) and decoded_response[pos].isspace(): pos += 1
                    if pos >= len(decoded_response): break
                    obj, end = decoder.raw_decode(decoded_response, pos)
                    pos = end
                    
                    if isinstance(obj, dict) and obj.get('id') == message_id and 'output' in obj:
                        raw_output = obj['output']
                        # Extract content between our markers
                        if "__JSON_START__" in raw_output and "__JSON_END__" in raw_output:
                            start = raw_output.find("__JSON_START__") + len("__JSON_START__")
                            end = raw_output.find("__JSON_END__")
                            return raw_output[start:end].strip()
                        return raw_output
                except json.JSONDecodeError:
                    break
            return None

        except Exception as e:
            log.error(f"Error running script on Unreal Engine: {e}")
            self.disconnect()
            return None