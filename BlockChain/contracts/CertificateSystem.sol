// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CertificateSystem {
    struct Certificate {
        string recipientName;
        string courseName;
        uint256 issueDate;
        bool isValid;
    }

    mapping(bytes32 => Certificate) public certificates;
    address public owner;

    event CertificateIssued(bytes32 indexed certificateId, string recipientName, string courseName);
    event CertificateRevoked(bytes32 indexed certificateId);

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the owner can perform this action");
        _;
    }

    function issueCertificate(string memory _recipientName, string memory _courseName) public onlyOwner returns (bytes32) {
        bytes32 certificateId = keccak256(abi.encodePacked(_recipientName, _courseName, block.timestamp));
        certificates[certificateId] = Certificate(_recipientName, _courseName, block.timestamp, true);
        emit CertificateIssued(certificateId, _recipientName, _courseName);
        return certificateId;
    }

    function validateCertificate(bytes32 _certificateId) public view returns (bool) {
        return certificates[_certificateId].isValid;
    }

    function revokeCertificate(bytes32 _certificateId) public onlyOwner {
        require(certificates[_certificateId].isValid, "Certificate is not valid or does not exist");
        certificates[_certificateId].isValid = false;
        emit CertificateRevoked(_certificateId);
    }
}